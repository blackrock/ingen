//  Mock RunService — simulates `python -m ingen` over the configured model. It walks the real
//  generate() stage order per interface (read → pre_process → [post_process] → format → validate →
//  write), streaming timestamped log lines and stage transitions through onEvent, and resolves with
//  a RunRecord. Validation outcomes come from the ValidationService so the run reflects the actual
//  configured expectations (incl. blocker abort / critical row-drop semantics).

import { RunService } from '../services/runService.js';
import { makeId } from '../utils/id.js';
import { MockValidationAdapter } from './mockValidationAdapter.js';

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const now = () => new Date().toISOString();

const STAGE_LABEL = {
  read: 'Reading sources',
  pre_process: 'Pre-processing',
  post_process: 'Post-processing',
  format: 'Formatting',
  validate: 'Validation',
  write: 'Writing output',
};

export class MockRunAdapter extends RunService {
  constructor(validationService = new MockValidationAdapter()) {
    super();
    this.validation = validationService;
  }

  async simulate(model, overrides = {}, handlers = {}) {
    const { onEvent, isCancelled } = handlers;
    const startedAt = now();
    const startMs = Date.now();
    const logs = [];
    const stages = [];

    const emit = (e) => {
      const evt = { ts: now(), ...e };
      logs.push(evt);
      onEvent?.(evt);
    };

    const selected = overrides.interfaces?.length
      ? model.interfaceOrder.filter((n) => overrides.interfaces.includes(n))
      : model.interfaceOrder;

    const validation = await this.validation.evaluate(model, selected);

    emit({ type: 'log', level: 'info', message: `Run started for "${model.meta.name}" (${selected.length} interface(s))` });
    if (overrides.run_date) emit({ type: 'log', level: 'info', message: `run_date = ${overrides.run_date}` });

    let aborted = 0;
    let cancelled = false;

    for (const name of selected) {
      if (isCancelled?.()) { cancelled = true; break; }
      const iface = model.interfacesByName[name];
      emit({ type: 'log', level: 'info', interface: name, message: `Generating interface '${name}'` });

      const order = ['read', 'pre_process'];
      if (iface.post_processing?.length) order.push('post_process');
      order.push('format', 'validate', 'write');

      let interfaceAborted = false;
      for (const stage of order) {
        if (isCancelled?.()) { cancelled = true; break; }
        if (interfaceAborted) { stages.push({ interface: name, stage, status: 'skipped', durationMs: 0 }); continue; }

        const t0 = Date.now();
        emit({ type: 'stage', interface: name, stage, status: 'running' });
        emit({ type: 'log', level: 'info', interface: name, stage, message: `${STAGE_LABEL[stage]}…` });
        await sleep(110 + Math.floor(Math.random() * 90));

        let status = 'ok';
        if (stage === 'read') {
          emit({ type: 'log', level: 'info', interface: name, stage, message: `Read ${iface.sources?.length ?? 0} source(s)` });
        } else if (stage === 'validate') {
          const rs = validation.results.filter((r) => r.interface === name);
          const blocker = rs.some((r) => r.status === 'failed' && r.severity === 'blocker');
          const failed = rs.some((r) => r.status === 'failed');
          const warned = rs.some((r) => r.status === 'warning');
          if (blocker) {
            status = 'failed';
            interfaceAborted = true;
            emit({ type: 'log', level: 'error', interface: name, stage, message: 'Blocker validation failed — aborting interface' });
          } else if (failed || warned) {
            status = 'warning';
            emit({ type: 'log', level: 'warn', interface: name, stage, message: `${rs.filter((r) => r.status !== 'passed').length} expectation(s) flagged` });
          } else {
            emit({ type: 'log', level: 'info', interface: name, stage, message: `${rs.length} expectation(s) passed` });
          }
        } else if (stage === 'write') {
          const out = iface.output?.type ?? 'none';
          emit({ type: 'log', level: 'info', interface: name, stage, message: `Wrote output (${out})` });
        }

        emit({ type: 'stage', interface: name, stage, status });
        stages.push({ interface: name, stage, status, durationMs: Date.now() - t0 });
      }

      if (interfaceAborted) aborted += 1;
      if (cancelled) break;
    }

    const finishedAt = now();
    const durationMs = Date.now() - startMs;
    let status = 'success';
    if (cancelled || aborted === selected.length) status = 'failed';
    else if (aborted > 0) status = 'partial';

    emit({ type: 'log', level: status === 'success' ? 'info' : 'warn', message: `Run ${status} in ${(durationMs / 1000).toFixed(2)}s` });

    return {
      runId: makeId('run'),
      configId: model.meta.id,
      configName: model.meta.name,
      status,
      startedAt,
      finishedAt,
      durationMs,
      stages,
      logs,
      validation,
      overrides,
    };
  }
}

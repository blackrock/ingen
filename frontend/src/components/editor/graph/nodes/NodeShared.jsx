//  Shared primitives used by all custom node types.

export const PropTable = ({ rows }) => {
  const visible = rows.filter((r) => r.value != null && r.value !== '');
  if (!visible.length) return null;
  return (
    <div className="custom-node__props">
      {visible.map(({ key, value }) => (
        <div key={key} className="custom-node__prop-row">
          <span className="custom-node__prop-key">{key}</span>
          <span className="custom-node__prop-val">{String(value)}</span>
        </div>
      ))}
    </div>
  );
};

export const CustomNodeHeader = ({ icon, title, type, color }) => (
  <div className="custom-node__header">
    <div className="custom-node__icon-box" style={{ backgroundColor: `${color}18`, color }}>
      {icon}
    </div>
    <div style={{ minWidth: 0 }}>
      <div className="custom-node__title">{title}</div>
      <div className="custom-node__type">{type}</div>
    </div>
  </div>
);

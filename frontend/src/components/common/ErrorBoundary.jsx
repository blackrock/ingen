//  InGen Studio — ErrorBoundary
//
//  Catches render/lifecycle exceptions anywhere in the tree below it so a single bad record or a
//  thrown component never blanks the whole SPA. React only supports class components as error
//  boundaries (no hook equivalent), hence the class. Offers a reset that re-renders the children and
//  a link back to the configs list.

import { Component } from 'react';
import Link from 'next/link';

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    // Keep a breadcrumb in the console for debugging; no external logging in scope.
    console.error('Unhandled UI error:', error, info?.componentStack);
  }

  reset = () => this.setState({ error: null });

  render() {
    if (this.state.error) {
      return (
        <div className="placeholder" role="alert">
          <h2>Something went wrong.</h2>
          <p className="muted">{this.state.error.message || String(this.state.error)}</p>
          <div className="wtopbar__right">
            <button className="btn btn--accent" onClick={this.reset}>Try again</button>
            <Link className="btn btn--ghost-dark" href="/" onClick={this.reset}>Back to configs</Link>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

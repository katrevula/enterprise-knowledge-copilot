import { render, screen } from '@testing-library/react';
import App from './App';

test('renders the copilot chat shell', () => {
  render(<App />);
  expect(screen.getByText('Enterprise Knowledge Copilot')).toBeInTheDocument();
  expect(screen.getByLabelText('Message')).toBeInTheDocument();
});


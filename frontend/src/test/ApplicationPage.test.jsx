import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from '../App';
import LoginPage from '../login/LoginPage';
import ProfilePage from '../profile/ProfilePage';
import SearchPage from '../search/SearchPage';
import ApplicationPage from '../application/ApplicationPage';
// import ApplicationPage from '../application/ApplicationPage';

// 1. Renders app title
test('renders app title', () => {
	render(<App />);
	expect(screen.getByText(/Application Tracking System/i)).toBeInTheDocument();
});

// 2. Renders login inputs
test('renders login form inputs', () => {
	render(<LoginPage side={() => {}} />);
	expect(screen.getByLabelText(/Username/i)).toBeInTheDocument();
	expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
});

// 3. Renders login button
test('renders login button', () => {
	render(<LoginPage side={() => {}} />);
	expect(screen.getByText('Login')).toBeInTheDocument();
});

// 4. Signup tab shows signup form
test('clicking signup tab reveals signup form', () => {
	render(<LoginPage side={() => {}} />);
	fireEvent.click(screen.getByText('Signup'));
	expect(screen.getByText('Sign Up')).toBeInTheDocument();
});

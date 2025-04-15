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


// 5. Profile displays full name
test('renders profile full name', () => {
	render(<ProfilePage profile={{ fullName: 'Alice' }} updateProfile={() => {}} />);
	expect(screen.getByText('Alice')).toBeInTheDocument();
});

// 6. Profile renders skills
test('renders user skills', () => {
	const profile = {
		fullName: '',
		skills: [{ label: 'React', value: 'react' }],
		job_levels: [], locations: []
	};
	render(<ProfilePage profile={profile} updateProfile={() => {}} />);
	expect(screen.getByText('React')).toBeInTheDocument();
});


// 7. Search page input renders
test('renders search input on search page', () => {
	render(<SearchPage />);
	expect(screen.getByPlaceholderText(/Enter job title/i)).toBeInTheDocument();
});

// 8. Search button exists
test('renders search button', () => {
	render(<SearchPage />);
	expect(screen.getByText('Search')).toBeInTheDocument();
});

// 9. Renders application page button
test('renders add application button', () => {
	render(<ApplicationPage />);
	expect(screen.getByText('+ Add New Application')).toBeInTheDocument();
});


// 10. Application list renders a job title
test('renders application job title', () => {
	const applications = [{ id: 1, jobTitle: 'Frontend Dev', companyName: '', location: '', date: '', status: '1' }];
	render(<ApplicationPage applicationList={applications} handleCardClick={() => {}} selectedApplication={null} handleUpdateDetails={() => {}} handleDeleteApplication={() => {}} />);
	expect(screen.getByText('Frontend Dev')).toBeInTheDocument();
});

// 11. Application list renders company name
test('renders application company', () => {
	const applications = [{ id: 1, jobTitle: '', companyName: 'Meta', location: '', date: '', status: '1' }];
	render(<ApplicationPage applicationList={applications} handleCardClick={() => {}} selectedApplication={null} handleUpdateDetails={() => {}} handleDeleteApplication={() => {}} />);
	expect(screen.getByText('Meta')).toBeInTheDocument();
});

// 12. Application list renders location
test('renders application location', () => {
	const applications = [{ id: 1, jobTitle: '', companyName: '', location: 'Remote', date: '', status: '1' }];
	render(<ApplicationPage applicationList={applications} handleCardClick={() => {}} selectedApplication={null} handleUpdateDetails={() => {}} handleDeleteApplication={() => {}} />);
	expect(screen.getByText('Remote')).toBeInTheDocument();
});

// 13. Application list renders status label
test('renders status label', () => {
	const applications = [{ id: 1, jobTitle: '', companyName: '', location: '', date: '', status: '3' }];
	render(<ApplicationPage applicationList={applications} handleCardClick={() => {}} selectedApplication={null} handleUpdateDetails={() => {}} handleDeleteApplication={() => {}} />);
	expect(screen.getByText('Applied')).toBeInTheDocument();
});


// 14. Clicking login does not crash
test('login button can be clicked', () => {
	render(<LoginPage side={() => {}} />);
	fireEvent.click(screen.getByText('Login'));
});

// 15. Clicking search button triggers event
test('clicking search button does not crash', () => {
	render(<SearchPage />);
	fireEvent.click(screen.getByText('Search'));
});


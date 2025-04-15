import './static/App.css';

import React from 'react';
import Sidebar from './sidebar/Sidebar';
import ApplicationPage from './application/ApplicationPage';
import SearchPage from './search/SearchPage';
import LoginPage from './login/LoginPage';
import ManageResumePage from './resume/ManageResumePage';
import ProfilePage from './profile/ProfilePage';
import OnBoardingForm from './onboarding/OnBoardingForm';
import axios from 'axios';
import MatchesPage from './matches/MatchesPage';
import Joyride from 'react-joyride';

export default class App extends React.Component {
	constructor(props) {
		super(props);
		let mapRouter = {
			SearchPage: <SearchPage />,
			ApplicationPage: <ApplicationPage />,
			LoginPage: <LoginPage />,
			ManageResumePage: <ManageResumePage />,
			ProfilePage: <ProfilePage />,
			MatchesPage: <MatchesPage />
		};
		this.state = {
			currentPage: <LoginPage />,
			mapRouter: mapRouter,
			sidebar: false,
			userProfile: null,
			showOnboarding: false,
			runTour: false,
			steps: [
				{
					target: '.sidebar',
					content: 'This is your navigation menu. Use it to access different areas of the application.',
					placement: 'right',
					disableBeacon: true
				},
				{
					target: '.main',
					content: 'This main area displays your current view based on what you select from the sidebar.',
					placement: 'left'
				}
			]
		};
		this.sidebarHandler = this.sidebarHandler.bind(this);
		this.updateProfile = this.updateProfile.bind(this);
		this.completeOnboarding = this.completeOnboarding.bind(this);
	}

	updateProfile = (profile) => {
		console.log('Update Request: ', profile);
		this.setState({
			userProfile: profile,
			currentPage: <ProfilePage profile={profile} updateProfile={this.updateProfile} />
		});
	};

	async componentDidMount() {
		if (localStorage.getItem('token')) {
			const userId = localStorage.getItem('userId');
			try {
				const res = await axios.get('http://127.0.0.1:5000/getProfile', {
					headers: {
						userid: userId,
						Authorization: `Bearer ${localStorage.getItem('token')}`
					}
				});
				console.log("Profile data from API:", res.data);
				this.sidebarHandler(res.data);
			} catch (err) {
				console.error("Error fetching profile:", err.message);
				// Try to use stored profile from localStorage as fallback
				const storedProfile = localStorage.getItem('userProfile');
				if (storedProfile) {
					console.log("Using stored profile from localStorage");
					this.sidebarHandler(JSON.parse(storedProfile));
				}
			}
		}
	}

	sidebarHandler = (user) => {
		console.log("User data received:", user);
		
		// Check if this is a new user who needs onboarding
		const isNewUser = !user.skills || !Array.isArray(user.skills) || user.skills.length === 0;
		console.log("Is new user:", isNewUser, "Skills:", user.skills);
		
		this.setState({
			sidebar: true,
			userProfile: user,
			showOnboarding: isNewUser,
			currentPage: isNewUser ? 
				<OnBoardingForm profile={user} completeOnboarding={this.completeOnboarding} /> : 
				<ProfilePage profile={user} updateProfile={this.updateProfile.bind(this)} />
		});
	};
	
	completeOnboarding = (updatedProfile) => {
		this.setState({
			showOnboarding: false,
			userProfile: updatedProfile,
			currentPage: <ProfilePage profile={updatedProfile} updateProfile={this.updateProfile.bind(this)} />,
			runTour: true
		});
	};

	handleLogout = () => {
		localStorage.removeItem('token');
		localStorage.removeItem('userId');
		this.setState({
			sidebar: false
		});
	};

	switchPage(pageName) {
		const currentPage =
			pageName == 'ProfilePage' ? (
				<ProfilePage
					profile={this.state.userProfile}
					updateProfile={this.updateProfile.bind(this)}
				/>
			) : (
				this.state.mapRouter[pageName]
			);
		this.setState({
			currentPage: currentPage
		});
	}

	render() {
		var app;
		
		// Enhanced tour steps with more detailed information
		const appSteps = [
			{
				target: '.sidebar',
				content: 'This is your navigation menu. Use it to access different areas of the application.',
				placement: 'right',
				disableBeacon: true
			},
			{
				target: '.profile-section',
				content: 'View and update your profile information here. Add your skills and preferences to get better job recommendations.',
				placement: 'left'
			},
			{
				target: '.applications-section',
				content: 'Keep track of all your job applications in one place. See status updates and organize your job search.',
				placement: 'bottom'
			},
			{
				target: '.analyses-section',
				content: 'Review past analyses of how well your profile matches with job requirements.',
				placement: 'left'
			}
		];
		
		if (this.state.sidebar) {
			app = (
				<div className='main-page'>
					<Sidebar
						switchPage={this.switchPage.bind(this)}
						handleLogout={this.handleLogout}
					/>
					<div className='main'>
						<div className='content'>
							<div className=''>
								<h1
									className='text-center'
									style={{ marginTop: '2%', fontWeight: '300' }}
								>
									Application Tracking System
								</h1>
							</div>
							{this.state.currentPage}
						</div>
					</div>
					
					{/* Joyride tour */}
					<Joyride
						steps={appSteps}
						run={this.state.runTour}
						continuous={true}
						showProgress={true}
						showSkipButton={true}
						styles={{
							options: {
								primaryColor: '#296E85'
							}
						}}
						callback={(data) => {
							if (data.status === 'finished' || data.status === 'skipped') {
								this.setState({ runTour: false });
							}
						}}
					/>
				</div>
			);
		} else {
			app = (
				<div className='main-page'>
					<div className='main'>
						<div className='content'>
							<h1
								className='text-center'
								style={{
									marginTop: 30,
									padding: 0.4 + 'em',
									fontWeight: '300'
								}}
							>
								Application Tracking System
							</h1>
							<div className=''>
							</div>
							<LoginPage side={this.sidebarHandler} />
						</div>
					</div>
				</div>
			);
		}
		return app;
	}
}

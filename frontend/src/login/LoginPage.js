import React, { Component } from 'react';
import { Tabs, Tab } from 'react-bootstrap';
import { getToken, signUp, storeToken } from '../api/loginHandler';

export default class LoginPage extends Component {
	constructor(props) {
		super(props);

		this.state = {};
	}

	handleLogin = (uname, pwd) => {
		console.log('Login click');
		let obj = { username: uname, password: pwd };
	
		getToken(obj)
			.then((res) => {
				console.log("Login API Response:", res);
	
				if (!res || res.error) {
					throw new Error('Wrong username or password');
				}
	
				// Ensure res.profile exists
				if (!res.profile) {
					console.error("Profile data missing in API response:", res);
					alert("Error: Profile data is missing!");
					return;
				}
	
				storeToken({ ...res, userId: res.profile.id });
				this.props.side(res.profile);
			})
			.catch((error) => {
				console.error("Login Error:", error);
				alert('Error while logging in! Wrong username or password');
			});
	};
	

	handleSignup = (fullname, uname, pwd) => {
		console.log('Signup click');
		let obj = {
			username: uname,
			password: pwd,
			fullName: fullname
		};
		
		signUp(obj)
			.then((res) => {
				console.log("Signup successful:", res);
				
				// Automatically log in after successful signup
				this.handleLogin(uname, pwd);
			})
			.catch((error) => {
				console.error("Signup error:", error);
				alert('Error while signing up!');
			});
	};

	handleSignupGoogle = () => {
		window.open('http://localhost:5000/users/signupGoogle'); // Google oauth url
	};

	componentDidMount() {
		if (localStorage.getItem('token') === null) {
			const query = new URLSearchParams(window.location.search);
			const token = query.get('token');
			const expiry = query.get('expiry');
			const userId = query.get('userId');
			let obj = {
				token: token,
				expiry: expiry,
				userId: userId
			};
			if (token) {
				storeToken(obj);
				window.location.assign('http://localhost:3000/application-tracking-system'); // changing back to this to avoid leaking data such as access tokens from the url
			}
		}
	}

	render() {
		return (
			<div className='auth-wrapper' style={this.authWrapper}>
				<div className='auth-inner' style={this.authInner}>
					{/* <div className="logindiv" style={this.divStyle}> */}
					<Tabs
						defaultActiveKey='login'
						id='logintab'
						className='mx-auto'
						style={{ paddingLeft: '25%' }}
					>
						<Tab eventKey='login' title='Login'>
							<form>
								<div className='form-group my-4'>
									<label>Username</label>
									<input
										type='text'
										className='form-control'
										id='uname'
										placeholder='Enter username'
									/>
								</div>

								<div className='form-group my-4'>
									<label>Password</label>
									<input
										type='password'
										className='form-control'
										id='pwd'
										placeholder='Enter password'
									/>
								</div>
								<div className='d-flex justify-content-center'>
									<button
										type='submit'
										onClick={(e) => {
											e.preventDefault();
											let uname = document.querySelector('#uname').value;
											let pwd = document.querySelector('#pwd').value;
											this.handleLogin(uname, pwd);
										}}
										className='custom-btn px-3 py-2 mx-2'
										// style={{ marginRight: 10 }}
									>
										Login
									</button>

									<button
										onClick={() => {
											this.handleSignupGoogle();
										}}
										className='custom-btn px-3 py-2 mx-2'
									>
										Google Login
									</button>
								</div>
							</form>
						</Tab>
						<Tab eventKey='signup' title='Signup'>
							<form>
								<div className='form-group my-4'>
									<label>Full name</label>
									<input
										type='text'
										className='form-control'
										id='fullname'
										placeholder='Full name'
									/>
								</div>
								<div className='form-group my-4'>
									<label>Username</label>
									<input
										type='text'
										className='form-control'
										id='suname'
										placeholder='Enter username'
									/>
								</div>
								<div className='form-group my-4'>
									<label>Password</label>
									<input
										type='password'
										className='form-control'
										id='spwd'
										placeholder='Enter password'
									/>
								</div>
								<div className='d-flex justify-content-center'>
									<button
										type='submit'
										onClick={(e) => {
											e.preventDefault();
											let name = document.querySelector('#fullname').value;
											let uname = document.querySelector('#suname').value;
											let pwd = document.querySelector('#spwd').value;
											this.handleSignup(name, uname, pwd);
										}}
										className='custom-btn px-3 py-2 mx-2'
									>
										Sign Up
									</button>

									<button
										onClick={() => {
											this.handleSignupGoogle();
										}}
										className='custom-btn px-3 py-2 mx-2'
									>
										Google Signup
									</button>
								</div>
							</form>
						</Tab>
					</Tabs>
				</div>
			</div>
		);
	}

	divStyle = {
		width: '50vw'
	};

	authWrapper = {
		display: 'flex',
		justifyContent: 'center',
		flexDirection: 'column',
		textAlign: 'left',
		marginTop: '5vh'
	};

	authInner = {
		width: '450px',
		margin: 'auto',
		background: '#ffffff',
		boxShadow: '0px 14px 80px rgba(34, 35, 58, 0.2)',
		padding: '40px 55px 45px 55px',
		borderRadius: '15px',
		transition: 'all .3s'
	};
}

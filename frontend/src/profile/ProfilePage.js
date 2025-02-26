import React, { useEffect, useState } from 'react';
import LocationModal from './CustomModal';
import SkillsModal from './CustomModal';
import ExperienceLevelModal from './CustomModal';
import JobModeModal from './CustomModal';
import ProfileModal from './CustomProfileModal';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { CONSTANTS } from '../data/Constants';
import {
	faEnvelope,
	faLocationDot,
	faPenToSquare,
	faPhone
} from '@fortawesome/free-solid-svg-icons';

const ProfilePage = (props) => {
	const [locationModalOpen, setLocationModalOpen] = useState(false);
	const [skillsModalOpen, setSkillsModalOpen] = useState(false);
	const [ExpLevelModalOpen, setExpLevelModalOpen] = useState(false);
	const [profileModalOpen, setProfileModalOpen] = useState(false);
	const [jobModeModalOpen, setJobModeModalOpen] = useState(false);
	const [pastAnalyses, setPastAnalyses] = useState([]);
	const [selectedAnalysis, setSelectedAnalysis] = useState(null);
	const [applicationCount, setApplicationCount] = useState(0);
	const [applicationsByStatus, setApplicationsByStatus] = useState({
		applied: 0,
		rejected: 0,
		waitingReferral: 0,
		wishList: 0
	});

	const profile = props.profile;
	/**
	 * Given a full name string, the method returns initials or the abbreviated name of the user profile in terms of initial letters of the first and last word of the full name
	 * @param {String} fullName This string is the full name of the user
	 * @returns The abbreviated name string
	 */
	function getUserInitials(fullName) {
		if (fullName && fullName.trim().length > 0) {
			const arr = fullName.trim().split(' ');
			let initials = arr[0].substring(0, 1);
			if (arr.length > 1) {
				initials += arr[arr.length - 1].substring(0, 1);
			}
			return <span style={{ fontSize: 60, letterSpacing: 1.2 }}>{initials}</span>;
		}
		return (
			<span style={{ fontSize: 60, letterSpacing: 1.2 }}>
				<FontAwesomeIcon icon='fa-solid fa-user' style={{ color: '#fbfcfe' }} />
			</span>
		);
	}

	useEffect(() => {
		// Fetch past analyses from backend
		const fetchAnalyses = async () => {
			try {
				const response = await fetch('http://127.0.0.1:5000/analyses', {
					headers: {
						'Authorization': 'Bearer ' + localStorage.getItem('token'),
						'Access-Control-Allow-Origin': 'http://127.0.0.1:3000',
						'Access-Control-Allow-Credentials': 'true'
					}
				});
				
				if (!response.ok) {
					throw new Error('Failed to fetch analyses');
				}
				
				const data = await response.json();
				setPastAnalyses(data);
			} catch (error) {
				console.error('Error fetching analyses:', error);
			}
		};

		// Fetch applications and analyses
		Promise.all([
			fetch('http://127.0.0.1:5000/applications', {
				headers: {
					'Authorization': 'Bearer ' + localStorage.getItem('token'),
					'Access-Control-Allow-Origin': 'http://127.0.0.1:3000',
					'Access-Control-Allow-Credentials': 'true'
				}
			}),
			fetchAnalyses()
		])
		.then(async ([applicationsResponse]) => {
			const applicationsData = await applicationsResponse.json();
			setApplicationCount(applicationsData.length);
			// Count applications by status
			const counts = {
				applied: applicationsData.filter(app => app.status === '3').length,
				rejected: applicationsData.filter(app => app.status === '4').length,
				waitingReferral: applicationsData.filter(app => app.status === '2').length,
				wishList: applicationsData.filter(app => app.status === '1').length
			};
			setApplicationsByStatus(counts);
		})
		.catch(error => {
			console.error('Error fetching data:', error);
		});
	}, []);

	return (
		<div className='container-fluid' style={{ marginLeft: '6%', marginTop: '2%' }}>
			<div className='row gx-5'>
				<div className='col-3'>
					<div
						className='card p-4 mb-4'
						style={{
							boxShadow: '0px 5px 12px 0px rgba(0,0,0,0.1)',
							marginRight: '20px'
						}}
					>
						<FontAwesomeIcon
							icon={faPenToSquare}
							size='1x'
							onClick={() => setProfileModalOpen(true)}
							cursor='pointer'
							style={{ position: 'absolute', top: '15', right: '15' }}
						/>
						<div className='text-center my-3'>
							<div
								className='text-center mt-3 d-inline-flex justify-content-center align-items-center'
								style={{
									height: '200px',
									width: '200px',
									borderRadius: '100%',
									backgroundColor: '#296E85',
									color: '#fff',
									boxShadow: '0px 5px 12px 10px rgba(0,0,0,0.1)'
								}}
							>
								{getUserInitials(profile.fullName)}
							</div>
						</div>
						<div className='text-center mt-3'>
							<h3 className='card-title mb-1'>
								{profile[CONSTANTS.PROFILE.NAME]
									? profile[CONSTANTS.PROFILE.NAME]
									: ''}
							</h3>
							<span style={{ fontSize: 20 }}>
								{profile[CONSTANTS.PROFILE.UNIVERSITY]
									? profile[CONSTANTS.PROFILE.UNIVERSITY]
									: ''}
							</span>
						</div>
						<hr className='my-4' />
						<div className='row gy-4'>
							<div className='col-12 d-flex align-items-center'>
								<FontAwesomeIcon icon={faEnvelope} size='1x' />
								<span className='mx-2'>
									{profile[CONSTANTS.PROFILE.EMAIL]
										? profile[CONSTANTS.PROFILE.EMAIL]
										: ''}
								</span>
							</div>
							<div className='col-12 d-flex align-items-center'>
								<FontAwesomeIcon icon={faPhone} size='1x' />
								<span className='mx-2'>
									{profile[CONSTANTS.PROFILE.CONTACT]
										? profile[CONSTANTS.PROFILE.CONTACT]
										: ''}
								</span>
							</div>
							<div className='col-12 d-flex align-items-center'>
								<FontAwesomeIcon icon={faLocationDot} size='1x' />
								<span className='mx-2'>
									{profile[CONSTANTS.PROFILE.ADDRESS]
										? profile[CONSTANTS.PROFILE.ADDRESS]
										: ''}
								</span>
							</div>
						</div>
					</div>
				</div>
				<div className='col-5'>
					<div
						className='card p-4 mb-4'
						style={{
							boxShadow: '0px 5px 12px 0px rgba(0,0,0,0.1)',
							marginRight: '20px'
						}}
					>
						<div className='card-body'>
							<div className='d-flex justify-content-between px-0 mb-3'>
								<h4 className='card-title mb-0 mx-1'>Skills</h4>
								<div className='text-right'>
									<FontAwesomeIcon
										icon={faPenToSquare}
										size='1x'
										onClick={() => setSkillsModalOpen(true)}
										cursor='pointer'
									/>
								</div>
							</div>
							<div className='d-flex flex-wrap'>
								{profile[CONSTANTS.PROFILE.SKILLS]?.map((ele, index) => (
									<span
										className='badge rounded-pill m-1 py-2 px-3'
										style={{
											border: '2px solid',
											// backgroundColor: "#0096c7",
											backgroundColor: '#296e85',
											fontSize: 16,
											fontWeight: 'normal'
										}}
										key={index}
									>
										{ele.label}
									</span>
								))}
							</div>
						</div>
					</div>
					<div
						className='card p-4 mb-4'
						style={{
							boxShadow: '0px 5px 12px 0px rgba(0,0,0,0.1)',
							marginRight: '20px'
						}}
					>
						<div className='card-body'>
							<div className='d-flex justify-content-between px-0 mb-3'>
								<h4 className='card-title mb-0 mx-1'>Experience Level</h4>
								<FontAwesomeIcon
									icon={faPenToSquare}
									size='1x'
									onClick={() => setExpLevelModalOpen(true)}
									cursor='pointer'
								/>
							</div>
							<div className='d-flex flex-wrap'>
								{profile[CONSTANTS.PROFILE.EXPERIENCE_LEVEL]?.map((ele, index) => (
									<span
										className='badge rounded-pill m-1 py-2 px-3'
										style={{
											border: '2px solid',
											// backgroundColor: "#0096c7",
											backgroundColor: '#296e85',
											fontSize: 16,
											fontWeight: 'normal'
										}}
										key={index}
									>
										{ele.label}
									</span>
								))}
							</div>
						</div>
					</div>
					<div
						className='card p-4 mb-4'
						style={{
							boxShadow: '0px 5px 12px 0px rgba(0,0,0,0.1)',
							marginRight: '20px'
						}}
					>
						<div className='card-body'>
							<div className='d-flex justify-content-between px-0 mb-3'>
								<h4 className='card-title mb-0 mx-1'>Locations</h4>
								<FontAwesomeIcon
									icon={faPenToSquare}
									size='1x'
									onClick={() => setLocationModalOpen(true)}
									cursor='pointer'
								/>
							</div>
							<div className='d-flex flex-wrap'>
								{profile[CONSTANTS.PROFILE.PREFERRED_LOCATIONS]?.map(
									(ele, index) => (
										<span
											className='badge rounded-pill m-1 py-2 px-3'
											style={{
												border: '2px solid',
												// backgroundColor: "#0096c7",
												backgroundColor: '#296e85',
												fontSize: 16,
												fontWeight: 'normal'
											}}
											key={index}
										>
											{ele.label}
										</span>
									)
								)}
							</div>
						</div>
					</div>

					{/* Applications Card */}
					<div className='card p-4 mb-4' style={{ 
						boxShadow: '0px 5px 12px 0px rgba(0,0,0,0.1)',
						marginRight: '20px'
					}}>
						<div className='card-body'>
							<div className='d-flex justify-content-between px-0 mb-3'>
								<h4 className='card-title mb-0 mx-1'>Applications</h4>
							</div>
							<div className='d-flex align-items-center mb-4'>
								<h2 className='mb-0' style={{ color: '#296e85' }}>{applicationCount}</h2>
								<span className='ms-2 text-muted'>Total Applications</span>
							</div>

							{/* Status Grid */}
							<div className="row g-3">
								<div className="col-6">
									<div className="card" style={{ 
										boxShadow: '0px 3px 8px 0px rgba(0,0,0,0.1)',
										borderRadius: '10px',
										border: 'none'
									}}>
										<div className="card-body text-center p-3">
											<h3 style={{ color: '#296E85' }}>{applicationsByStatus.applied}</h3>
											<h6 className="card-title mb-0">Applied</h6>
										</div>
									</div>
								</div>
								<div className="col-6">
									<div className="card" style={{ 
										boxShadow: '0px 3px 8px 0px rgba(0,0,0,0.1)',
										borderRadius: '10px',
										border: 'none'
									}}>
										<div className="card-body text-center p-3">
											<h3 style={{ color: '#296E85' }}>{applicationsByStatus.rejected}</h3>
											<h6 className="card-title mb-0">Rejected</h6>
										</div>
									</div>
								</div>
								<div className="col-6">
									<div className="card" style={{ 
										boxShadow: '0px 3px 8px 0px rgba(0,0,0,0.1)',
										borderRadius: '10px',
										border: 'none'
									}}>
										<div className="card-body text-center p-3">
											<h3 style={{ color: '#296E85' }}>{applicationsByStatus.waitingReferral}</h3>
											<h6 className="card-title mb-0">Waiting for Referral</h6>
										</div>
									</div>
								</div>
								<div className="col-6">
									<div className="card" style={{ 
										boxShadow: '0px 3px 8px 0px rgba(0,0,0,0.1)',
										borderRadius: '10px',
										border: 'none'
									}}>
										<div className="card-body text-center p-3">
											<h3 style={{ color: '#296E85' }}>{applicationsByStatus.wishList}</h3>
											<h6 className="card-title mb-0">Wish List</h6>
										</div>
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>
				<div className='col-4'>
					<div className='card' style={{ 
						boxShadow: '0px 5px 12px 0px rgba(0,0,0,0.1)',
						height: 'calc(100vh - 40px)',
						overflowY: 'auto'
					}}>
						<div className='card-body p-4'>
							<div className='d-flex justify-content-between px-0 mb-4'>
								<h4 className='card-title mb-0'>Past Job Match Analyses</h4>
							</div>
							
							{selectedAnalysis && (
								<div className="alert alert-info mb-4">
									<div className="d-flex justify-content-between align-items-center mb-3">
										<span>
											Analysis for "{selectedAnalysis.searchTerm}"
										</span>
										<button 
											className="btn btn-sm btn-outline-info"
											onClick={() => setSelectedAnalysis(null)}
										>
											Hide Details
										</button>
									</div>
									<small className="d-block text-muted mb-3">
										Analyzed on {selectedAnalysis.date}
									</small>
									
									<div className="card">
										<div className="card-body">
											<h6>Match Overview</h6>
											<div className="progress mb-3">
												<div 
													className="progress-bar" 
													role="progressbar" 
													style={{ 
														width: `${selectedAnalysis.comparison.overallMatch}%`,
														backgroundColor: '#296E85'
													}}
													aria-valuenow={selectedAnalysis.comparison.overallMatch} 
													aria-valuemin="0" 
													aria-valuemax="100"
												>
													{selectedAnalysis.comparison.overallMatch}%
												</div>
											</div>
											
											<div className="row g-3">
												<div className="col-6">
													<h6>Matching Skills</h6>
													<ul className="list-group list-group-flush">
														{selectedAnalysis.comparison.matchingSkills.map((skill, index) => (
															<li key={index} className="list-group-item text-success">
																<i className="fas fa-check-circle me-2"></i>{skill}
															</li>
														))}
													</ul>
												</div>
												<div className="col-6">
													<h6>Missing Skills</h6>
													<ul className="list-group list-group-flush">
														{selectedAnalysis.comparison.missingSkills.map((skill, index) => (
															<li key={index} className="list-group-item text-danger">
																<i className="fas fa-times-circle me-2"></i>{skill}
															</li>
														))}
													</ul>
												</div>
											</div>
										</div>
									</div>
								</div>
							)}

							<div className="list-group">
								{pastAnalyses.map(analysis => (
									<button
										key={analysis.id}
										className={`list-group-item list-group-item-action p-3 mb-2 ${
											selectedAnalysis?.id === analysis.id ? 'active' : ''
										}`}
										onClick={() => setSelectedAnalysis(
											selectedAnalysis?.id === analysis.id ? null : analysis
										)}
										style={{
											borderRadius: '8px',
											border: '1px solid #dee2e6'
										}}
									>
										<div className="d-flex w-100 justify-content-between align-items-center">
											<h5 className="mb-1">{analysis.searchTerm}</h5>
											<span className={`badge ${
												analysis.comparison.overallMatch >= 70 ? 'bg-success' :
												analysis.comparison.overallMatch >= 40 ? 'bg-warning' :
												'bg-danger'
											}`}>
												{analysis.comparison.overallMatch}% Match
											</span>
										</div>
										<small className="text-muted">{analysis.date}</small>
									</button>
								))}
							</div>

							{pastAnalyses.length === 0 && (
								<div className="text-center mt-4">
									<p className="text-muted">No analyses yet</p>
									<p className="small text-muted">
										Try searching for jobs to see how well your profile matches!
									</p>
								</div>
							)}
						</div>
					</div>
				</div>
			</div>
			{locationModalOpen && (
				<LocationModal
					name={CONSTANTS.PROFILE.PREFERRED_LOCATIONS}
					options={CONSTANTS.COUNTRIES}
					profile={props.profile}
					// setProfile={setProfile}
					setModalOpen={setLocationModalOpen}
					updateProfile={props.updateProfile}
				/>
			)}
			{skillsModalOpen && (
				<SkillsModal
					name={CONSTANTS.PROFILE.SKILLS}
					options={CONSTANTS.SKILLS}
					profile={props.profile}
					// setProfile={setProfile}
					setModalOpen={setSkillsModalOpen}
					updateProfile={props.updateProfile}
				/>
			)}
			{ExpLevelModalOpen && (
				<ExperienceLevelModal
					name={CONSTANTS.PROFILE.EXPERIENCE_LEVEL}
					options={CONSTANTS.EXPERIENCE_LEVEL}
					profile={props.profile}
					// setProfile={setProfile}
					setModalOpen={setExpLevelModalOpen}
					updateProfile={props.updateProfile}
				/>
			)}
			{jobModeModalOpen && (
				<JobModeModal
					name={CONSTANTS.PROFILE.JOB_MODE}
					options={CONSTANTS.JOB_MODES}
					profile={props.profile}
					// setProfile={setProfile}
					setModalOpen={setJobModeModalOpen}
					updateProfile={props.updateProfile}
				/>
			)}
			{profileModalOpen && (
				<ProfileModal
					profile={props.profile}
					// setProfile={setProfile}
					setModalOpen={setProfileModalOpen}
					updateProfile={props.updateProfile}
				/>
			)}
			{/* <JobDescription /> */}
		</div>
	);
};

export default ProfilePage;

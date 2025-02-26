import React, { useState, useEffect } from 'react';
import Spinner from '../spinners/Spinner';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';

const Recommendations = () => {
	const [recommendedJobs, setRecommendedJobs] = useState([]);
	const [isFetchingJobs, setIsFetchingJobs] = useState(true);
	const [fetchError, setFetchError] = useState(null);
	const [wishList, setWishList] = useState(
		localStorage.getItem('wishList') ? JSON.parse(localStorage.getItem('wishList')) : {}
	);

	useEffect(() => {
		const lastJobFetchResults = localStorage.getItem('lastJobFetchResults');
		if (lastJobFetchResults) {
			setRecommendedJobs(JSON.parse(localStorage.getItem('lastJobFetchResults')));
			setIsFetchingJobs(false);
		} else {
			fetchRecommendations();
		}
	}, []);

	const fetchRecommendations = async () => {
		try {
			setIsFetchingJobs(true);
			const response = await fetch('http://localhost:5001/getRecommendations', {
				headers: {
					Authorization: 'Bearer ' + localStorage.getItem('token'),
					'Access-Control-Allow-Origin': 'http://localhost:3000',
					'Access-Control-Allow-Credentials': 'true'
				},
				method: 'GET'
			});
			const data = await response.json();
			if (data && data['error']) {
				throw new Error(data['error']);
			} else {
				localStorage.setItem('lastJobFetch', new Date().getTime());
				localStorage.setItem('lastJobFetchResults', JSON.stringify(data));
				setRecommendedJobs(data);
			}
		} catch (error) {
			setFetchError(error.message);
		} finally {
			setIsFetchingJobs(false);
		}
	};

	return (
		<div>
			<h2 class='d-flex justify-content-center my-5'>Recommended Jobs</h2>
			<table
				classname='table my-4'
				style={{
					boxShadow: '0px 5px 12px 0px rgba(0,0,0,0.1)',
					marginTop: 30,
					marginLeft: '10%'
				}}
			>
				<thead>
					<tr>
						<th
							className='p-3'
							style={{
								fontSize: 18,
								fontWeight: '500',
								backgroundColor: '#2a6e85',
								color: '#fff'
							}}
						>
							Company Name
						</th>
						<th
							className='p-3'
							style={{
								fontSize: 18,
								fontWeight: '500',
								backgroundColor: '#2a6e85',
								color: '#fff'
							}}
						>
							Job Title
						</th>
						<th
							className='p-3'
							style={{
								fontSize: 18,
								fontWeight: '500',
								backgroundColor: '#2a6e85',
								color: '#fff'
							}}
						>
							Link
						</th>
						<th
							className='p-3'
							style={{
								fontSize: 18,
								fontWeight: '500',
								backgroundColor: '#2a6e85',
								color: '#fff'
							}}
						>
							Location
						</th>

						<th
							className='p-3'
							style={{
								fontSize: 18,
								fontWeight: '500',
								backgroundColor: '#2a6e85',
								color: '#fff'
							}}
						></th>
					</tr>
				</thead>
				<tbody>
					{!isFetchingJobs &&
						!fetchError &&
						recommendedJobs &&
						recommendedJobs.map((job, index) => (
							<tr key={index}>
								<td className='p-3'>{job.companyName}</td>
								<td className='p-3'>{job.jobTitle}</td>
								<a
									target='_blank'
									rel='noopener noreferrer'
									href={job.data_share_url}
								>
									<button
										type='button'
										class='btn btn-primary d-flex align-items-center'
										style={{
											backgroundColor: '#2a6e85',
											margin: '5px',
											width: '100px',
											verticalAlign: 'middle'
										}}
									>
										Job Link
									</button>
								</a>
								{/* <a className='p-3' href='{job.data_share_url}'>Job Link</a> */}
								<td className='p-3'>{job.location}</td>
								<td className='p-3'>
									<button
										type='button'
										class='btn btn-dark'
										onClick={() => {
											wishList[index] = wishList[index] ? false : true;
											setWishList({ ...wishList });
											localStorage.setItem(
												'wishList',
												JSON.stringify(wishList)
											);
										}}
									>
										<FontAwesomeIcon
											icon={`${
												wishList[index] ? 'fa-solid' : 'fa-regular'
											} fa-bookmark`}
											size='1x'
											cursor='pointer'
										/>
									</button>
								</td>
							</tr>
						))}
					{isFetchingJobs && (
						<tr key='0'>
							<td className='p-3 text-center' colSpan={3}>
								<Spinner otherCSS='me-5' />
								Finding most relevant jobs for you!
							</td>
						</tr>
					)}
					{!isFetchingJobs &&
						!fetchError &&
						(!recommendedJobs || recommendedJobs.length === 0) && (
							<tr key='0'>
								<td className='p-3 text-center' colSpan={4}>
									No Matches found
								</td>
							</tr>
						)}
					{!isFetchingJobs && fetchError && (
						<tr key='0'>
							<td className='p-3 text-center' colSpan={4}>
								{fetchError}. Re-try after updating your profile with your skills,
								preferred location and desired experience level details.
							</td>
						</tr>
					)}
				</tbody>
			</table>
		</div>
	);
};

export default Recommendations;

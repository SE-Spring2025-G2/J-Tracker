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
        fetchRecommendations();
    }, []);

    const fetchRecommendations = async () => {
        try {
            setIsFetchingJobs(true);
            setFetchError(null);

            console.log('Fetching recommendations...'); // Debug log
            const token = localStorage.getItem('token');
            console.log('Using token:', token); // Debug log

            const response = await fetch('http://localhost:5000/getRecommendations', {
                headers: {
                    'Authorization': 'Bearer ' + token,
                    'Content-Type': 'application/json'
                },
                method: 'GET'
            });

            const data = await response.json();
            console.log('Received response:', data); // Debug log

            if (!response.ok) {
                throw new Error(data.error || 'Failed to fetch recommendations');
            }

            if (Array.isArray(data)) {
                console.log('Setting jobs:', data); // Debug log
                setRecommendedJobs(data);
            } else if (data.message) {
                console.log('Setting error:', data.message); // Debug log
                setFetchError(data.message);
            } else {
                throw new Error('Invalid response format');
            }
        } catch (error) {
            console.error('Error fetching recommendations:', error);
            setFetchError(error.message);
        } finally {
            setIsFetchingJobs(false);
        }
    };

    // Add debug useEffect
    useEffect(() => {
        console.log('Current recommendedJobs:', recommendedJobs);
        console.log('Current fetchError:', fetchError);
        console.log('Current isFetchingJobs:', isFetchingJobs);
    }, [recommendedJobs, fetchError, isFetchingJobs]);

    return (
        <div>
            <h2 className='d-flex justify-content-center my-5'>Recommended Jobs</h2>
            <table
                className='table my-4'
                style={{
                    boxShadow: '0px 5px 12px 0px rgba(0,0,0,0.1)',
                    marginTop: 30,
                    marginLeft: '10%',
                    width: '80%'
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
                        >
                            Save
                        </th>
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
                                <td className='p-3'>
                                    <a
                                        target='_blank'
                                        rel='noopener noreferrer'
                                        href={job.data_share_url}
                                    >
                                        <button
                                            type='button'
                                            className='btn btn-primary'
                                            style={{
                                                backgroundColor: '#2a6e85',
                                                margin: '5px',
                                                width: '100px'
                                            }}
                                        >
                                            Job Link
                                        </button>
                                    </a>
                                </td>
                                <td className='p-3'>{job.location}</td>
                                <td className='p-3'>
                                    <button
                                        type='button'
                                        className='btn btn-dark'
                                        onClick={() => {
                                            const newWishList = { ...wishList };
                                            newWishList[index] = !wishList[index];
                                            setWishList(newWishList);
                                            localStorage.setItem('wishList', JSON.stringify(newWishList));
                                        }}
                                    >
                                        <FontAwesomeIcon
                                            icon={`${wishList[index] ? 'fa-solid' : 'fa-regular'} fa-bookmark`}
                                            size='1x'
                                            style={{ cursor: 'pointer' }}
                                        />
                                    </button>
                                </td>
                            </tr>
                        ))}
                    {isFetchingJobs && (
                        <tr>
                            <td colSpan={5} className='text-center p-3'>
                                <Spinner otherCSS='me-2' />
                                Finding most relevant jobs for you...
                            </td>
                        </tr>
                    )}
                    {!isFetchingJobs && fetchError && (
                        <tr>
                            <td colSpan={5} className='text-center p-3 text-danger'>
                                {fetchError}
                            </td>
                        </tr>
                    )}
                    {!isFetchingJobs &&
                        !fetchError &&
                        (!recommendedJobs || recommendedJobs.length === 0) && (
                            <tr>
                                <td colSpan={5} className='text-center p-3'>
                                    No matches found. Please update your profile with skills and preferences.
                                </td>
                            </tr>
                        )}
                </tbody>
            </table>
        </div>
    );
};

export default Recommendations;
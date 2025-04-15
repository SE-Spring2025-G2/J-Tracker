import React, { useState, useEffect } from 'react';
import Spinner from '../spinners/Spinner';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';

const Recommendations = () => {
    const [recommendedJobs, setRecommendedJobs] = useState([]);
    const [isFetchingJobs, setIsFetchingJobs] = useState(true);
    const [fetchError, setFetchError] = useState(null);
    const [addingToWishlist, setAddingToWishlist] = useState({}); //this is to initiate the spinner
    const [wishlistSuccess, setWishlistSuccess] = useState({}); //to determine if the job has been wishlisted or not
    const [fadeOutJobs, setFadeOutJobs] = useState({});
    // const [wishList, setWishList] = useState(
    //     localStorage.getItem('wishList') ? JSON.parse(localStorage.getItem('wishList')) : {}
    // );

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

            const response = await fetch('http://localhost:5000/jobs/shared', {
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

    // when a user clicks on the wishlist button, we add the 
    // job to the users application tracker tab and then remove this 
    // job from the recommended jobs pool
    const jobWishList = async (job) => {
        try {
            //set loading state for this previous job
            setAddingToWishlist(prev => ({ ...prev, [job.id]: true }));

            const token = localStorage.getItem('token');
            const response = await fetch('http://localhost:5000/wishlist', {
                method: 'POST',
                headers: {
                    'Authorization': 'Bearer ' + token,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ jobId: job.id })
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to add job to wishlist');
            }

            console.log('Job added to wishlist:', data);
            
            // Show success message for this job
            setWishlistSuccess(prev => ({ ...prev, [job.id]: true }));
            
            // Start fade out animation after 1 second
            setTimeout(() => {
                setFadeOutJobs(prev => ({ ...prev, [job.id]: true }));
                
                // Remove job from list after fade completes (4 seconds total)
                setTimeout(() => {
                    setRecommendedJobs(prev => prev.filter(j => j.id !== job.id));
                    // Clean up state for this job
                    setWishlistSuccess(prev => {
                        const newState = { ...prev };
                        delete newState[job.id];
                        return newState;
                    });
                    setFadeOutJobs(prev => {
                        const newState = { ...prev };
                        delete newState[job.id];
                        return newState;
                    });
                    setAddingToWishlist(prev => {
                        const newState = { ...prev };
                        delete newState[job.id];
                        return newState;
                    });
                }, 3000); // 3 seconds for fade effect
            }, 1000); // 1 second delay before starting fade

        } catch (error) {
            console.error('Error adding job to wishlist:', error);
            alert('Failed to add job to wishlist: ' + error.message);
            // Reset loading state on error
            setAddingToWishlist(prev => ({ ...prev, [job.id]: false }));
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
                            Sr. No.
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
                            Applied By
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
                                <td className='p-3'>{index}</td>
                                <td className='p-3'>{job.companyName}</td>
                                <td className='p-3'>{job.jobTitle}</td>
                                <td className='p-3'>
                                    <a
                                        target='_blank'
                                        rel='noopener noreferrer'
                                        href={job.jobLink}
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
                                <td className='p-3'>{job.appliedBy}</td>
                                <td className='p-3'>
                                    <button
                                        type='button'
                                        className='btn btn-primary'
                                        style={{
                                            backgroundColor: wishlistSuccess[job.id] ? '#28a745' : '#2a6e85',
                                            width: '150px'
                                        }}
                                        onClick={() => jobWishList(job)}
                                        disabled={addingToWishlist[job.id] || wishlistSuccess[job.id]}
                                    >
                                        {addingToWishlist[job.id] ? (
                                            <>
                                                <Spinner otherCSS="me-2" size="sm" />
                                                Adding...
                                            </>
                                        ) : wishlistSuccess[job.id] ? (
                                            <>Added to wishlist! ✓</>
                                        ) : (
                                            <>Add to wishlist</>
                                        )}
                                    </button>
                                </td>
                            </tr>
                        ))}
                    {isFetchingJobs && (
                        <tr>
                            <td colSpan={7} className='text-center p-3'>
                                <Spinner otherCSS='me-2' />
                                Finding most relevant jobs for you...
                            </td>
                        </tr>
                    )}
                    {!isFetchingJobs && fetchError && (
                        <tr>
                            <td colSpan={7} className='text-center p-3 text-danger'>
                                {fetchError}
                            </td>
                        </tr>
                    )}
                    {!isFetchingJobs &&
                        !fetchError &&
                        (!recommendedJobs || recommendedJobs.length === 0) && (
                            <tr>
                                <td colSpan={7} className='text-center p-3'>
                                    No new jobs found at the moment. Take a break!
                                </td>
                            </tr>
                        )}
                </tbody>
            </table>
        </div>
    );
};

export default Recommendations;
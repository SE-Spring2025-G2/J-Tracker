import React, { useState } from 'react';
import { CONSTANTS } from '../data/Constants';
import Select from 'react-select';

const OnBoardingForm = ({ profile, completeOnboarding }) => {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    fullName: profile?.fullName || '',
    email: profile?.email || '',
    phone_number: profile?.phone_number || '',
    address: profile?.address || '',
    institution: profile?.institution || '',
    skills: profile?.skills || [],
    job_levels: profile?.job_levels || [],
    locations: profile?.locations || []
  });
  
  console.log("OnboardingForm initialized with profile:", profile);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleSelectChange = (selectedOptions, action) => {
    setFormData({
      ...formData,
      [action.name]: selectedOptions || []
    });
  };

  const nextStep = () => {
    setStep(step + 1);
  };

  const prevStep = () => {
    setStep(step - 1);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      console.log("Submitting onboarding data:", formData);
      
      const response = await fetch('http://127.0.0.1:5000/updateProfile', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(formData)
      });
      
      if (!response.ok) {
        throw new Error('Failed to update profile');
      }
      
      // Update user preferences in localStorage
      localStorage.setItem('userProfile', JSON.stringify(formData));
      
      console.log("Onboarding completed successfully");
      completeOnboarding(formData);
    } catch (error) {
      console.error('Error updating profile:', error);
      
      // Even if the server update fails, we can still continue with the app
      // by storing data locally and updating the UI
      localStorage.setItem('userProfile', JSON.stringify(formData));
      console.log("Proceeding despite server error");
      completeOnboarding(formData);
      
      alert('There was an error communicating with the server, but your profile has been saved locally.');
    }
  };

  const renderStep = () => {
    switch (step) {
      case 1:
        return (
          <div className="card p-4">
            <h2>Welcome to J-Tracker!</h2>
            <p className="mb-4">Let's set up your profile to get started. We'll collect some basic information about you in the next few steps.</p>
            <h4>Step 1: Personal Information</h4>
            <div className="form-group my-3">
              <label>Full Name</label>
              <input
                type="text"
                className="form-control"
                name="fullName"
                value={formData.fullName}
                onChange={handleInputChange}
                placeholder="Enter your full name"
              />
            </div>
            <div className="form-group my-3">
              <label>Email</label>
              <input
                type="email"
                className="form-control"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="Enter your email"
              />
            </div>
            <div className="form-group my-3">
              <label>Phone Number</label>
              <input
                type="tel"
                className="form-control"
                name="phone_number"
                value={formData.phone_number}
                onChange={handleInputChange}
                placeholder="Enter your phone number"
              />
            </div>
            <div className="form-group my-3">
              <label>Address</label>
              <input
                type="text"
                className="form-control"
                name="address"
                value={formData.address}
                onChange={handleInputChange}
                placeholder="Enter your address"
              />
            </div>
            <div className="form-group my-3">
              <label>Institution/University</label>
              <input
                type="text"
                className="form-control"
                name="institution"
                value={formData.institution}
                onChange={handleInputChange}
                placeholder="Enter your institution or university"
              />
            </div>
            <div className="d-flex justify-content-end mt-4">
              <button 
                className="custom-btn px-4 py-2" 
                onClick={nextStep}
                disabled={!formData.fullName || !formData.email}
              >
                Next
              </button>
            </div>
          </div>
        );
      case 2:
        return (
          <div className="card p-4">
            <h4>Step 2: Skills & Experience</h4>
            <div className="form-group my-3">
              <label>Your Skills</label>
              <Select
                isMulti
                name="skills"
                options={CONSTANTS.SKILLS}
                value={formData.skills}
                onChange={(selected, action) => handleSelectChange(selected, { name: 'skills' })}
                className="basic-multi-select"
                classNamePrefix="select"
                placeholder="Select your skills..."
              />
              <small className="form-text text-muted">
                Select the skills you have. This helps us recommend relevant job opportunities.
              </small>
            </div>
            <div className="form-group my-3">
              <label>Experience Level</label>
              <Select
                isMulti
                name="job_levels"
                options={CONSTANTS.EXPERIENCE_LEVEL}
                value={formData.job_levels}
                onChange={(selected, action) => handleSelectChange(selected, { name: 'job_levels' })}
                className="basic-multi-select"
                classNamePrefix="select"
                placeholder="Select your experience level..."
              />
            </div>
            <div className="d-flex justify-content-between mt-4">
              <button 
                className="btn btn-secondary px-4 py-2" 
                onClick={prevStep}
              >
                Previous
              </button>
              <button 
                className="custom-btn px-4 py-2" 
                onClick={nextStep}
                disabled={formData.skills.length === 0}
              >
                Next
              </button>
            </div>
          </div>
        );
      case 3:
        return (
          <div className="card p-4">
            <h4>Step 3: Job Preferences</h4>
            <div className="form-group my-3">
              <label>Preferred Locations</label>
              <Select
                isMulti
                name="locations"
                options={CONSTANTS.COUNTRIES}
                value={formData.locations}
                onChange={(selected, action) => handleSelectChange(selected, { name: 'locations' })}
                className="basic-multi-select"
                classNamePrefix="select"
                placeholder="Select your preferred locations..."
              />
              <small className="form-text text-muted">
                Where would you like to work? This helps us recommend jobs in your preferred locations.
              </small>
            </div>
            <div className="mt-4">
              <h5>You're almost done!</h5>
              <p>
                After completing your profile, we'll guide you through the main features of the application:
              </p>
              <ul>
                <li>Track and manage your job applications</li>
                <li>Search for jobs that match your skills</li>
                <li>Get AI-powered job recommendations</li>
                <li>Analyze your resume against job descriptions</li>
              </ul>
            </div>
            <div className="d-flex justify-content-between mt-4">
              <button 
                className="btn btn-secondary px-4 py-2" 
                onClick={prevStep}
              >
                Previous
              </button>
              <button 
                className="custom-btn px-4 py-2" 
                onClick={handleSubmit}
              >
                Complete Setup
              </button>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="container mt-4">
      <div className="row justify-content-center">
        <div className="col-md-8">
          {renderStep()}
          
          <div className="progress mt-4">
            <div 
              className="progress-bar" 
              role="progressbar" 
              style={{ 
                width: `${(step / 3) * 100}%`,
                backgroundColor: '#296E85'
              }} 
              aria-valuenow={(step / 3) * 100} 
              aria-valuemin="0" 
              aria-valuemax="100"
            >
              Step {step} of 3
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OnBoardingForm;
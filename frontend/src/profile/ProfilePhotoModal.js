import React, { useState } from 'react';
import { Modal, Button, Form } from 'react-bootstrap';
import axios from 'axios';

const ProfilePhotoModal = ({ setModalOpen, updateProfile, currentProfile }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadError, setUploadError] = useState('');

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleUpload = () => {
    if (!selectedFile) {
      setUploadError('Please select a file.');
      return;
    }

    const formData = new FormData();
    // Use the key 'profilePhoto' to match the backend endpoint
    formData.append('profilePhoto', selectedFile);

    axios
      .post('http://localhost:5001/profilePhoto', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: `Bearer ${currentProfile.id}` // Adjust as needed for your auth system
        }
      })
      .then((response) => {
        // After a successful POST, call the GET endpoint to fetch the profile photo URL.
        axios.get('http://localhost:5001/profilePhoto', {
          headers: {
            Authorization: `Bearer ${currentProfile.id}`
          }
        })
        .then((getResponse) => {
          const photoUrl = getResponse.data.url;
          updateProfile({ ...currentProfile, profilePhoto: photoUrl });
          setModalOpen(false);
        })
        .catch((err) => {
          console.error("Error fetching profile photo URL:", err);
          setUploadError('Upload succeeded, but failed to retrieve photo URL.');
        });
      })
      .catch((error) => {
        console.error("Upload error:", error);
        setUploadError('Upload failed. Please try again.');
      });
  };

  return (
    <Modal show onHide={() => setModalOpen(false)} centered>
      <Modal.Header closeButton>
        <Modal.Title>Upload Profile Photo</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form>
          <Form.Group controlId="formProfilePhoto">
            <Form.Label>Select an image</Form.Label>
            <Form.Control type="file" accept="image/*" onChange={handleFileChange} />
            {uploadError && <p style={{ color: 'red' }}>{uploadError}</p>}
          </Form.Group>
        </Form>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={() => setModalOpen(false)}>
          Cancel
        </Button>
        <Button variant="primary" onClick={handleUpload}>
          Upload
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default ProfilePhotoModal;

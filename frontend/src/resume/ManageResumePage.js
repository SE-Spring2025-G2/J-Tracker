import React, { Component } from 'react'
import $ from 'jquery'
import { Container, Row, Col, Card, Button, Alert, Modal } from 'react-bootstrap'

export default class ManageResumePage extends Component {
  constructor(props) {
    super(props)
    this.state = {
      fileName: '',
      fileuploadname: '',
      resumeDownloadContent: null,
      errorMessage: '',
      showError: false,
      isPdf: false
    }

    this.getFiles.bind(this);
  }

  getFiles() {
    $.ajax({
      url: 'http://127.0.0.1:5000/resume',
      method: 'GET',
      headers: {
        'Authorization': 'Bearer ' + localStorage.getItem('token'),
        'Access-Control-Allow-Origin': 'http://127.0.0.1:3000',
        'Access-Control-Allow-Credentials': 'true'
      },
      xhrFields: {
        responseType: 'blob'
      },
      credentials: 'include',
      success: (message, textStatus, response) => {
        const fileName = response.getResponseHeader('x-fileName');
        const contentType = message.type;
        const isPdf = contentType === 'application/pdf';

        this.setState({ 
          fileName: fileName,
          resumeDownloadContent: message,
          isPdf: isPdf
        });
        
        if (!isPdf && message.size > 0) {
          this.setState({
            errorMessage: 'The current resume is not a PDF file. Some functionality may be limited.',
            showError: true
          });
        }
      },
      error: (error) => {
        console.error('Error fetching resume:', error);
      }
    });
  }

  handleChange(event) {
    if (event.target.files.length > 0) {
      const file = event.target.files[0];
      const fileName = file.name;
      const fileType = file.type;
      
      if (fileType !== 'application/pdf') {
        this.setState({
          errorMessage: 'Only PDF files are supported. Please select a PDF file.',
          showError: true,
          fileuploadname: ''
        });
        // Reset the file input
        document.getElementById('file').value = '';
      } else {
        this.setState({ 
          fileuploadname: fileName,
          showError: false,
          errorMessage: ''
        });
      }
    }
  }

  uploadResume() {
    if (!this.state.fileuploadname) {
      this.setState({
        errorMessage: 'Please select a PDF file to upload',
        showError: true
      });
      return;
    }
    
    const fileInput = document.getElementById('file').files[0];
    
    if (fileInput.type !== 'application/pdf') {
      this.setState({
        errorMessage: 'Only PDF files are supported. Please select a PDF file.',
        showError: true
      });
      return;
    }

    this.setState({ fileName: this.state.fileuploadname });
    
    let formData = new FormData();
    formData.append('file', fileInput);

    $.ajax({
      url: 'http://127.0.0.1:5000/resume',
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + localStorage.getItem('token'),
        'Access-Control-Allow-Origin': 'http://127.0.0.1:3000',
        'Access-Control-Allow-Credentials': 'true'
      },
      data: formData,
      contentType: false,
      cache: false,
      processData: false,
      success: (msg) => {
        console.log(msg);
        // Reset the file input after successful upload
        document.getElementById('file').value = '';
        this.setState({
          fileuploadname: '',
          showError: false,
          errorMessage: ''
        });
        // Refresh files list after upload
        this.getFiles();
      },
      error: (error) => {
        this.setState({
          errorMessage: 'Error uploading resume. Please try again.',
          showError: true
        });
      }
    });
  }

  downloadResume() {
    if (!this.state.isPdf) {
      this.setState({
        errorMessage: 'The current file is not a PDF. Download may not work properly.',
        showError: true
      });
    }
    
    if (this.state.resumeDownloadContent) {
      const url = window.URL.createObjectURL(this.state.resumeDownloadContent);
      const a = document.createElement('a');
      a.href = url;
      a.download = this.state.fileName || 'resume.pdf';
      document.body.append(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } else {
      this.fetchAndDownloadResume();
    }
  }

  fetchAndDownloadResume() {
    $.ajax({
      url: 'http://127.0.0.1:5000/resume',
      method: 'GET',
      headers: {
        'Authorization': 'Bearer ' + localStorage.getItem('token'),
        'Access-Control-Allow-Origin': 'http://127.0.0.1:3000',
        'Access-Control-Allow-Credentials': 'true'
      },
      xhrFields: {
        responseType: 'blob'
      },
      success: (message, textStatus, response) => {
        const contentType = message.type;
        if (contentType !== 'application/pdf') {
          this.setState({
            errorMessage: 'The current file is not a PDF. Download may not work properly.',
            showError: true
          });
        }
        
        const url = window.URL.createObjectURL(message);
        const a = document.createElement('a');
        a.href = url;
        a.download = this.state.fileName || 'resume.pdf';
        document.body.append(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      },
      error: (error) => {
        this.setState({
          errorMessage: 'Error downloading resume. Please try again.',
          showError: true
        });
      }
    });
  }

  viewResume() {
    if (!this.state.isPdf) {
      this.setState({
        errorMessage: 'The current file is not a PDF. Viewing may not work properly.',
        showError: true
      });
    }
    
    if (this.state.resumeDownloadContent) {
      const url = window.URL.createObjectURL(this.state.resumeDownloadContent);
      window.open(url, '_blank');
    } else {
      this.fetchAndViewResume();
    }
  }

  fetchAndViewResume() {
    $.ajax({
      url: 'http://127.0.0.1:5000/resume',
      method: 'GET',
      headers: {
        'Authorization': 'Bearer ' + localStorage.getItem('token'),
        'Access-Control-Allow-Origin': 'http://127.0.0.1:3000',
        'Access-Control-Allow-Credentials': 'true'
      },
      xhrFields: {
        responseType: 'blob'
      },
      success: (message) => {
        const contentType = message.type;
        if (contentType !== 'application/pdf') {
          this.setState({
            errorMessage: 'The current file is not a PDF. Viewing may not work properly.',
            showError: true
          });
        }
        
        const url = window.URL.createObjectURL(message);
        window.open(url, '_blank');
      },
      error: (error) => {
        this.setState({
          errorMessage: 'Error viewing resume. Please try again.',
          showError: true
        });
      }
    });
  }

  closeError = () => {
    this.setState({
      showError: false
    });
  }

  componentDidMount() {
    // fetch the data only after this component is mounted
    this.getFiles();
  }

  render() {
    return (
      <Container style={{ marginTop: "20px" }}>
        <Row>
          <Col md={12}>
            <Card style={{
              marginLeft: "10%",
              borderColor: "#ccc",
              borderRadius: "5px",
              boxShadow: "0 4px 8px 0 rgba(0, 0, 0, 0.2)",
              padding: "20px"
            }}>
              <Card.Body>
                <h2>Upload Resume</h2>
                <div className="mb-4">
                  <input 
                    id="file" 
                    name="file" 
                    type="file" 
                    className="form-control" 
                    accept=".pdf"
                    onChange={this.handleChange.bind(this)}
                  />
                  <Button 
                    style={{ marginTop: "10px", backgroundColor: "#296E85" }}
                    onClick={this.uploadResume.bind(this)}
                  >
                    Upload
                  </Button>
                </div>

                <h2>Uploaded Documents</h2>
                <Card style={{ padding: "15px" }}>
                  <Row>
                    <Col sm={8}>
                      <h5>{this.state.fileName || "No resume uploaded"}</h5>
                    </Col>
                    <Col sm={4} className="text-right d-flex justify-content-end">
                      {this.state.fileName && (
                        <>
                          <Button 
                            variant="info"
                            style={{ marginRight: "10px" }}
                            onClick={this.viewResume.bind(this)}
                          >
                            View
                          </Button>
                          <Button 
                            variant="primary"
                            onClick={this.downloadResume.bind(this)}
                          >
                            Download
                          </Button>
                        </>
                      )}
                    </Col>
                  </Row>
                </Card>

                {/* Error Modal */}
                <Modal show={this.state.showError} onHide={this.closeError}>
                  <Modal.Header closeButton>
                    <Modal.Title>Error</Modal.Title>
                  </Modal.Header>
                  <Modal.Body>{this.state.errorMessage}</Modal.Body>
                  <Modal.Footer>
                    <Button variant="secondary" onClick={this.closeError}>
                      Close
                    </Button>
                  </Modal.Footer>
                </Modal>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    )
  }
}
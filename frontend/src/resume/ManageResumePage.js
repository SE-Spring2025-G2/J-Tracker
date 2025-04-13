import React, { Component } from 'react'
import $ from 'jquery'
import { Container, Row, Col, Card, Button } from 'react-bootstrap'

export default class ManageResumePage extends Component {
  constructor (props) {
    super(props)
    this.state = {
      fileName: '',
      fileuploadname: '',
      resumeDownloadContent: null
    }

    console.log("***");
    console.log(localStorage.getItem('token'));
    this.getFiles.bind(this);
  }

  getFiles () {
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
            console.log(response.getResponseHeader('x-fileName'))
            this.setState({ 
              fileName: response.getResponseHeader('x-fileName'),
              resumeDownloadContent: message
            });
          }
      })
  }

  handleChange(event) {
    var name = event.target.files[0].name;
    console.log(`Selected file - ${event.target.files[0].name}`);
    this.setState({ fileuploadname: name});
  }

  uploadResume() {
    this.setState({ fileName: this.state.fileuploadname});
    console.log(this.value);
    const fileInput = document.getElementById('file').files[0];
    //console.log(fileInput);

    let formData = new FormData();
    formData.append('file', fileInput);
    //console.log(formData);

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
        // Refresh files list after upload
        this.getFiles();
      }
    })
  }

  downloadResume() {
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
        const url = window.URL.createObjectURL(message);
        const a = document.createElement('a');
        a.href = url;
        a.download = this.state.fileName || 'resume.pdf';
        document.body.append(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      }
    });
  }

  viewResume() {
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
        const url = window.URL.createObjectURL(message);
        window.open(url, '_blank');
      }
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
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    )
  }
}
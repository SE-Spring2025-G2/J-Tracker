import React, { Component } from 'react';
import axios from 'axios';
// ... existing imports ...
import $ from 'jquery';

class SearchPage extends Component {
    state = {
        searchText: '',
        insights: null,
        loading: false,
        error: null,
        resumeContent: null,
        comparison: null,
        pastAnalyses: [],
        selectedAnalysis: null
    };

    componentDidMount() {
        this.fetchAnalyses();
        // Load past analyses from localStorage when component mounts
        const savedAnalyses = localStorage.getItem('pastAnalyses');
        if (savedAnalyses) {
            this.setState({ pastAnalyses: JSON.parse(savedAnalyses) });
        }
    }

    fetchResume = async () => {
        try {
            const response = await $.ajax({
                url: 'http://127.0.0.1:5000/resume',
                method: 'GET',
                headers: {
                    'Authorization': 'Bearer ' + localStorage.getItem('token'),
                    'Access-Control-Allow-Origin': 'http://127.0.0.1:3000',
                    'Access-Control-Allow-Credentials': 'true'
                },
                xhrFields: {
                    responseType: 'blob'
                }
            });

            const formData = new FormData();
            formData.append('resume', response);

            const parseResponse = await axios.post('http://127.0.0.1:5000/parse-resume', formData, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                    'Content-Type': 'multipart/form-data'
                }
            });

            return parseResponse.data;
        } catch (error) {
            console.error('Error fetching/parsing resume:', error);
            return null;
        }
    };

    handleSearch = async () => {
        if (!this.state.searchText) return;
        this.setState({ loading: true, error: null });

        try {
            const [resumeContent, insightsResponse] = await Promise.all([
                this.fetchResume(),
                axios.get('http://127.0.0.1:5000/search', {
                    params: { keywords: this.state.searchText },
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`,
                        'Content-Type': 'application/json'
                    }
                })
            ]);

            if (resumeContent && insightsResponse.data) {
                const comparisonResponse = await axios.post('http://127.0.0.1:5000/compare-resume', {
                    resume: resumeContent,
                    jobInsights: insightsResponse.data
                }, {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`,
                        'Content-Type': 'application/json'
                    }
                });

                const newAnalysis = {
                    id: Date.now(),
                    searchTerm: this.state.searchText,
                    date: new Date().toLocaleString(),
                    comparison: comparisonResponse.data,
                    insights: insightsResponse.data
                };

                // Save analysis to backend
                try {
                    const response = await fetch('http://127.0.0.1:5000/analyses', {
                        method: 'POST',
                        headers: {
                            'Authorization': 'Bearer ' + localStorage.getItem('token'),
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': 'http://127.0.0.1:3000',
                            'Access-Control-Allow-Credentials': 'true'
                        },
                        body: JSON.stringify(newAnalysis)
                    });
                    
                    if (!response.ok) {
                        throw new Error('Failed to save analysis');
                    }

                    // Fetch updated analyses list
                    this.fetchAnalyses();
                } catch (error) {
                    console.error('Error saving analysis:', error);
                }

                const updatedAnalyses = [...this.state.pastAnalyses, newAnalysis];
                localStorage.setItem('pastAnalyses', JSON.stringify(updatedAnalyses));
                this.setState({
                    insights: insightsResponse.data,
                    resumeContent,
                    comparison: comparisonResponse.data,
                    loading: false,
                    selectedAnalysis: null,
                    pastAnalyses: updatedAnalyses
                });
            } else {
                this.setState({
                    insights: insightsResponse.data,
                    loading: false,
                    error: resumeContent ? null : 'No resume found. Please upload a resume first.'
                });
            }
        } catch (error) {
            console.error('Search error:', error);
            this.setState({
                error: 'Failed to fetch insights. Please try again.',
                loading: false
            });
        }
    };

    handleAnalysisSelect = (analysis) => {
        this.setState({
            selectedAnalysis: analysis,
            insights: analysis.insights,
            comparison: analysis.comparison
        });
    };

    fetchAnalyses = async () => {
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
            this.setState({ pastAnalyses: data });
        } catch (error) {
            console.error('Error fetching analyses:', error);
        }
    };

    renderComparison() {
        const { comparison } = this.state;
        if (!comparison) return null;

        return (
            <div style={{ 
                display: 'flex',
                justifyContent: 'center',
                width: '100%'
            }}>
                <div className="card my-4" style={{ maxWidth: '800px', width: '100%' }}>
                    <div className="card-body">
                        <h4 className="text-primary">Resume Match Analysis</h4>
                        <div className="mb-4">
                            <h5>Overall Match: {comparison.overallMatch}%</h5>
                            <div className="progress mb-3">
                                <div 
                                    className="progress-bar" 
                                    role="progressbar" 
                                    style={{ width: `${comparison.overallMatch}%` }}
                                    aria-valuenow={comparison.overallMatch} 
                                    aria-valuemin="0" 
                                    aria-valuemax="100"
                                />
                            </div>
                        </div>

                        <div className="row">
                            <div className="col-md-6">
                                <h5>Matching Skills</h5>
                                <ul className="list-group">
                                    {comparison.matchingSkills.map((skill, index) => (
                                        <li key={index} className="list-group-item text-success">
                                            <i className="fas fa-check-circle me-2"></i>{skill}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                            <div className="col-md-6">
                                <h5>Missing Skills</h5>
                                <ul className="list-group">
                                    {comparison.missingSkills.map((skill, index) => (
                                        <li key={index} className="list-group-item text-danger">
                                            <i className="fas fa-times-circle me-2"></i>{skill}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        </div>

                        <div className="mt-4">
                            <h5>Recommendations</h5>
                            <ul className="list-group">
                                {comparison.recommendations.map((rec, index) => (
                                    <li key={index} className="list-group-item">
                                        <i className="fas fa-lightbulb me-2"></i>{rec}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    renderInsights() {
        const { insights } = this.state;
        if (!insights) return null;

        return (
            <div style={{ 
                display: 'flex',
                justifyContent: 'center',
                width: '100%'
            }}>
                <div className="card my-4" style={{ maxWidth: '800px', width: '100%' }}>
                    <div className="card-body">
                        <h4 className="text-primary">Job Role Insights</h4>
                        
                        <div className="mb-4">
                            <h5>Role Overview</h5>
                            <p>{insights.roleOverview}</p>
                        </div>

                        <div className="mb-4">
                            <h5>Technical Skills</h5>
                            {insights.technicalSkills.map((skillCategory, index) => (
                                <div key={index} className="mb-3">
                                    <h6>{skillCategory.category}</h6>
                                    <ul className="list-inline">
                                        {skillCategory.tools.map((tool, i) => (
                                            <li key={i} className="list-inline-item">
                                                <span className="badge bg-secondary me-2">{tool}</span>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            ))}
                        </div>

                        <div className="mb-4">
                            <h5>Soft Skills</h5>
                            <ul className="list-inline">
                                {insights.softSkills.map((skill, index) => (
                                    <li key={index} className="list-inline-item">
                                        <span className="badge bg-info me-2">{skill}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>

                        <div className="mb-4">
                            <h5>Recommended Certifications</h5>
                            <div className="row">
                                {insights.certifications.map((cert, index) => (
                                    <div key={index} className="col-md-6 mb-3">
                                        <div className="card h-100">
                                            <div className="card-body">
                                                <h6>{cert.name}</h6>
                                                <p className="small text-muted">
                                                    Provider: {cert.provider}<br/>
                                                    Level: {cert.level}
                                                </p>
                                                <p className="small">{cert.description}</p>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="mb-4">
                            <h5>Salary Ranges</h5>
                            <ul className="list-group">
                                <li className="list-group-item">Entry Level: {insights.salaryRange.entry}</li>
                                <li className="list-group-item">Mid Level: {insights.salaryRange.mid}</li>
                                <li className="list-group-item">Senior Level: {insights.salaryRange.senior}</li>
                            </ul>
                        </div>

                        <div className="mb-4">
                            <h5>Industry Trends</h5>
                            <ul className="list-group">
                                {insights.industryTrends.map((trend, index) => (
                                    <li key={index} className="list-group-item">{trend}</li>
                                ))}
                            </ul>
                        </div>

                        <div>
                            <h5>Learning Resources</h5>
                            <div className="row">
                                {insights.learningResources.map((resource, index) => (
                                    <div key={index} className="col-md-6 mb-3">
                                        <div className="card h-100">
                                            <div className="card-body">
                                                <h6>{resource.name}</h6>
                                                <p className="small text-muted">
                                                    Type: {resource.type}<br/>
                                                    Cost: {resource.cost}<br/>
                                                    Duration: {resource.duration}
                                                </p>
                                                <p className="small">{resource.description}</p>
                                                <a href={resource.url} target="_blank" rel="noopener noreferrer" 
                                                   className="btn btn-sm btn-primary">
                                                    Learn More
                                                </a>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    render() {
        return (
            <div className="d-flex">
                {/* Main Content */}
                <div style={{ 
                    marginLeft: '68px',
                    flex: '1',
                    padding: '20px',
                    position: 'relative',
                    zIndex: 0,
                    maxWidth: 'calc(100vw - 88px)'
                }}>
                    <div style={{ 
                        display: 'flex',
                        justifyContent: 'center',
                        width: '100%',
                        marginBottom: '20px'
                    }}>
                        <div className="input-group" style={{ maxWidth: '800px' }}>
                            <input
                                type="text"
                                className="form-control"
                                placeholder="Enter job title or role..."
                                value={this.state.searchText}
                                onChange={(e) => this.setState({ searchText: e.target.value })}
                            />
                            <button
                                className="btn btn-primary"
                                onClick={this.handleSearch}
                                disabled={this.state.loading}
                            >
                                {this.state.loading ? (
                                    <span>
                                        <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                                        Analyzing...
                                    </span>
                                ) : 'Search'}
                            </button>
                        </div>
                    </div>

                    {this.state.error && (
                        <div style={{ 
                            display: 'flex',
                            justifyContent: 'center',
                            width: '100%'
                        }}>
                            <div className="alert alert-danger" style={{ maxWidth: '800px', width: '100%' }}>
                                {this.state.error}
                            </div>
                        </div>
                    )}

                    {this.state.selectedAnalysis && (
                        <div style={{ 
                            display: 'flex',
                            justifyContent: 'center',
                            width: '100%'
                        }}>
                            <div className="alert alert-info d-flex justify-content-between align-items-center" 
                                 style={{ maxWidth: '800px', width: '100%' }}>
                                <span>
                                    Viewing analysis for "{this.state.selectedAnalysis.searchTerm}" from {this.state.selectedAnalysis.date}
                                </span>
                                <button 
                                    className="btn btn-sm btn-outline-info"
                                    onClick={() => this.setState({ selectedAnalysis: null })}
                                >
                                    Return to Current Search
                                </button>
                            </div>
                        </div>
                    )}

                    {this.renderComparison()}
                    {this.renderInsights()}

                    {/* Past Analyses Section as List */}
                    <div className="mt-4">
                        <h4 className="mb-3 text-center">Past Analyses</h4>
                        <div style={{ 
                            display: 'flex',
                            justifyContent: 'center',
                            width: '100%'
                        }}>
                            <div className="list-group" style={{ maxWidth: '800px', width: '100%' }}>
                                {this.state.pastAnalyses.map(analysis => (
                                    <button
                                        key={analysis.id}
                                        className={`list-group-item list-group-item-action ${
                                            this.state.selectedAnalysis?.id === analysis.id ? 'active' : ''
                                        }`}
                                        onClick={() => this.handleAnalysisSelect(analysis)}
                                    >
                                        <div className="d-flex w-100 justify-content-between">
                                            <h5 className="mb-1">{analysis.searchTerm}</h5>
                                            <small>{analysis.date}</small>
                                        </div>
                                        <p className="mb-1">Match: {analysis.comparison.overallMatch}%</p>
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}

export default SearchPage;
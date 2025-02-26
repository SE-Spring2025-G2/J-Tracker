import React, { Component } from 'react';
import axios from 'axios';

class SearchPage extends Component {
    state = {
        searchText: '',
        insights: null,
        loading: false,
        error: null
    };

    handleSearch = async () => {
        if (!this.state.searchText) return;

        this.setState({ loading: true, error: null });

        try {
            const response = await axios.get('http://127.0.0.1:5000/search', {
                params: { keywords: this.state.searchText },
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                    'Content-Type': 'application/json'
                }
            });

            console.log('API Response:', response.data);
            
            this.setState({
                insights: response.data,
                loading: false
            });
        } catch (error) {
            console.error('Search error:', error);
            this.setState({
                error: 'Failed to fetch insights. Please try again.',
                loading: false
            });
        }
    };

    renderInsights() {
        const { insights } = this.state;
        if (!insights) return null;

        return (
            <div className="card my-4">
                <div className="card-body">
                    <h3 className="card-title mb-4">Career Insights: {this.state.searchText}</h3>

                    {/* Role Overview */}
                    <div className="section mb-4">
                        <h4 className="text-primary">Role Overview</h4>
                        <p className="lead">{insights.roleOverview}</p>
                    </div>

                    {/* Prerequisites */}
                    {insights.prerequisites && (
                        <div className="section mb-4">
                            <h4 className="text-primary">Prerequisites</h4>
                            <div className="row">
                                <div className="col-md-4">
                                    <h5>Education</h5>
                                    <ul>
                                        {insights.prerequisites.education.map((item, index) => (
                                            <li key={index}>{item}</li>
                                        ))}
                                    </ul>
                                </div>
                                <div className="col-md-4">
                                    <h5>Experience</h5>
                                    <ul>
                                        {insights.prerequisites.experience.map((item, index) => (
                                            <li key={index}>{item}</li>
                                        ))}
                                    </ul>
                                </div>
                                <div className="col-md-4">
                                    <h5>Required Skills</h5>
                                    <ul>
                                        {insights.prerequisites.skills.map((item, index) => (
                                            <li key={index}>{item}</li>
                                        ))}
                                    </ul>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Technical Skills */}
                    <div className="section mb-4">
                        <h4 className="text-primary">Technical Skills</h4>
                        <div className="row">
                            {insights.technicalSkills.map((skillSet, index) => (
                                <div key={index} className="col-md-4 mb-3">
                                    <div className="card h-100">
                                        <div className="card-body">
                                            <h5 className="card-title">{skillSet.category}</h5>
                                            <ul className="list-unstyled">
                                                {skillSet.tools.map((tool, i) => (
                                                    <li key={i}>• {tool}</li>
                                                ))}
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Soft Skills */}
                    <div className="section mb-4">
                        <h4 className="text-primary">Soft Skills</h4>
                        <ul className="list-group">
                            {insights.softSkills.map((skill, index) => (
                                <li key={index} className="list-group-item">{skill}</li>
                            ))}
                        </ul>
                    </div>

                    {/* Certifications */}
                    <div className="section mb-4">
                        <h4 className="text-primary">Recommended Certifications</h4>
                        <div className="row">
                            {insights.certifications.map((cert, index) => (
                                <div key={index} className="col-md-4 mb-3">
                                    <div className="card h-100">
                                        <div className="card-body">
                                            <h5>{cert.name}</h5>
                                            <p><strong>Provider:</strong> {cert.provider}</p>
                                            <p><strong>Level:</strong> {cert.level}</p>
                                            <p>{cert.description}</p>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Project Ideas */}
                    <div className="section mb-4">
                        <h4 className="text-primary">Project Ideas</h4>
                        {insights.projectIdeas.map((project, index) => (
                            <div key={index} className="card mb-3">
                                <div className="card-body">
                                    <h5>{project.title}</h5>
                                    <p>{project.description}</p>
                                    <div className="mb-3">
                                        <strong>Technologies:</strong>
                                        <div className="d-flex flex-wrap gap-2 mt-2">
                                            {project.technologies.map((tech, i) => (
                                                <span key={i} className="badge bg-info">{tech}</span>
                                            ))}
                                        </div>
                                    </div>
                                    <div>
                                        <strong>Learning Outcomes:</strong>
                                        <ul>
                                            {project.learningOutcomes.map((outcome, i) => (
                                                <li key={i}>{outcome}</li>
                                            ))}
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Industry Trends */}
                    <div className="section mb-4">
                        <h4 className="text-primary">Industry Trends</h4>
                        <ul className="list-group">
                            {insights.industryTrends.map((trend, index) => (
                                <li key={index} className="list-group-item">{trend}</li>
                            ))}
                        </ul>
                    </div>

                    {/* Salary Range */}
                    <div className="section mb-4">
                        <h4 className="text-primary">Salary Ranges</h4>
                        <div className="card">
                            <div className="card-body">
                                <p><strong>Entry Level:</strong> {insights.salaryRange.entry}</p>
                                <p><strong>Mid Level:</strong> {insights.salaryRange.mid}</p>
                                <p><strong>Senior Level:</strong> {insights.salaryRange.senior}</p>
                                <div className="mt-3">
                                    <strong>Salary Factors:</strong>
                                    <ul>
                                        {insights.salaryRange.factors.map((factor, index) => (
                                            <li key={index}>{factor}</li>
                                        ))}
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Career Path */}
                    <div className="section mb-4">
                        <h4 className="text-primary">Career Path</h4>
                        <div className="card">
                            <div className="card-body">
                                <div className="mb-3">
                                    <h5>Entry Level</h5>
                                    <p>{insights.careerPath.entryLevel}</p>
                                </div>
                                <div className="mb-3">
                                    <h5>Mid Level</h5>
                                    <p>{insights.careerPath.midLevel}</p>
                                </div>
                                <div className="mb-3">
                                    <h5>Senior Level</h5>
                                    <p>{insights.careerPath.senior}</p>
                                </div>
                                <div>
                                    <h5>Advancement Opportunities</h5>
                                    <ul>
                                        {insights.careerPath.advancement.map((path, index) => (
                                            <li key={index}>{path}</li>
                                        ))}
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Learning Resources */}
                    <div className="section mb-4">
                        <h4 className="text-primary">Learning Resources</h4>
                        <div className="row">
                            {insights.learningResources.map((resource, index) => (
                                <div key={index} className="col-md-4 mb-3">
                                    <div className="card h-100">
                                        <div className="card-body">
                                            <h5>{resource.name}</h5>
                                            <p><strong>Type:</strong> {resource.type}</p>
                                            <p><strong>Cost:</strong> {resource.cost}</p>
                                            <p><strong>Duration:</strong> {resource.duration}</p>
                                            <p>{resource.description}</p>
                                            <a
                                                href={resource.url}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="btn btn-primary btn-sm"
                                            >
                                                Access Resource
                                            </a>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    render() {
        return (
            <div className="container mt-4">
                <div className="row justify-content-center">
                    <div className="col-md-8">
                        <div className="input-group mb-3">
                            <input
                                type="text"
                                className="form-control"
                                placeholder="Enter job title (e.g., Data Scientist)"
                                value={this.state.searchText}
                                onChange={(e) => this.setState({ searchText: e.target.value })}
                            />
                            <button
                                className="btn btn-primary"
                                onClick={this.handleSearch}
                                disabled={this.state.loading}
                            >
                                {this.state.loading ? 'Searching...' : 'Search'}
                            </button>
                        </div>

                        {this.state.error && (
                            <div className="alert alert-danger">{this.state.error}</div>
                        )}

                        {this.state.loading && (
                            <div className="text-center my-5">
                                <div className="spinner-border text-primary" role="status">
                                    <span className="visually-hidden">Loading...</span>
                                </div>
                            </div>
                        )}

                        {this.renderInsights()}
                    </div>
                </div>
            </div>
        );
    }
}

export default SearchPage;
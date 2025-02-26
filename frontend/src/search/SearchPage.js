import React, { Component } from "react";
import $ from "jquery";
import SearchCard from "./SearchCard";
import JobDescription from "../Modals/JobDescription";
import { Spinner } from "react-bootstrap";

const columns = [
  {
    label: "Company Name",
    id: "companyName",
  },
  {
    label: "Job Title",
    id: "jobTitle",
  },
  {
    label: "Location",
    id: "location",
  },
  {
    label: "Date",
    id: "date",
  },
  {
    label: "",
    id: "func",
  },
];

export default class SearchPage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      searchText: "",
      rows: [
        // {
        //   benefits: [
        //     "A stipend of $8,000 for ten weeks is available for up to two summer legal interns, but candidates are required to document attempts to secure funding through their law schools or external sources",
        //     "Any final stipend amount will be offset by amounts received through these external funding sources",
        //   ],
        //   companyName: "ACLU - Internships",
        //   date: "3 days ago",
        //   jobTitle: "Legal Internship Program",
        //   location: "  Raleigh, NC   ",
        //   qualifications: [
        //     "Completed first year of law school before the internship commences",
        //     "Ability to conduct thorough legal and factual research in a fast-paced litigation environment on short deadline, identify relevant authorities, and succinctly summarize findings",
        //     "Clear, direct writing and oral communication style, and ability to explain complex legal concepts in plain language",
        //     "Ability to take direction well and work collaboratively as part of a multidisciplinary team of other law students, supervising attorneys, and non-attorney staff members",
        //     "Deep respect for others' lived experiences, humility, and ability to work with, learn from, and interact respectfully with people from backgrounds different from your own",
        //     "Commitment to civil rights and civil liberties issues and the mission of the ACLU, especially if coupled with a desire to work in the public interest after law school",
        //   ],
        //   responsibilities: [
        //     "The internship is full-time and requires a 10-week commitment",
        //     "Conducting legal and policy research on a range of topics",
        //   ],
        // },
      ],
      salary: "",
      addedList: [],
      showJobDesc: false,
      selectedJob: null,
      searching: false,
    };
  }

  search() {
    if (!this.state.searchText) {
      window.alert("Search bar cannot be empty!!");
      return;
    }
    this.setState({ searching: true });
    $.ajax({
      url: "http://127.0.0.1:5001/search",
      method: "get",
      data: {
        keywords: this.state.searchText,
        salary: this.state.salary,
      },
      contentType: "application/json",
      success: (data) => {
        const res = data.map((d, i) => {
          return {
            id: i,
            jobTitle: d.jobTitle,
            companyName: d.companyName,
            location: d.location,
            date: d.date,
            qualifications: d.qualifications,
            benefits: d.benefits,
            responsibilities: d.responsibilities,
          };
        });
        this.setState({
          searching: false,
          rows: res,
        });
      },
      error: () => {
        window.alert("Error while fetching jobs. Please try again later");
        this.setState({
          searching: false,
        });
      },
    });
  }

  deleteTheApplication(id) {
    const newRows = this.state.rows.filter((app) => {
      return app.id !== id;
    });
    const newAddedList = this.state.addedList.filter((app) => {
      return app.id !== id;
    });
    this.setState({
      rows: newRows,
      addedList: newAddedList,
    });
  }

  // open the card modal according to the application in parameter
  showEditModal(job, mode) {
    // console.log(job)
    this.setState({
      showModal: true,
      job: job,
      modalMode: mode,
    });
  }

  handleCloseEditModal() {
    this.setState({
      showModal: false,
      job: null,
    });
  }

  addToWaitlist(job) {
    const newAddedList = this.state.addedList;
    newAddedList.push(job.id);
    // console.log(job)

    $.ajax({
      url: "http://127.0.0.1:5001/applications",
      method: "POST",
      data: JSON.stringify({
        application: job,
      }),
      headers: {
        Authorization: "Bearer " + localStorage.getItem("token"),
        "Access-Control-Allow-Origin": "http://127.0.0.1:3000",
        "Access-Control-Allow-Credentials": "true",
      },
      contentType: "application/json",
      success: (msg) => {
        console.log(msg);
        alert("Added item!");
      },
    });
    this.setState({
      addedList: newAddedList,
    });
  }

  removeFromWaitlist(job) {
    const newAddedList = this.state.addedList.filter((v) => {
      return v !== job.id;
    });
    this.setState({
      addedList: newAddedList,
    });
  }

  handleChange(event) {
    this.setState({ [event.target.id]: event.target.value });
  }

  setSalary(event) {
    this.setState({ [event.target.id]: event.target.value });
  }

  handleShowJobDesc(job) {
    this.setState({
      showJobDesc: !this.state.showJobDesc,
      selectedJob: job,
    });
  }

  render() {
    const rows = this.state.rows;

    let applicationModal = null;
    if (this.state.job) {
      applicationModal = (
        <SearchCard
          show={this.state.showModal}
          submitFunc={this.addToWaitlist.bind(this)}
          mode={this.state.modalMode}
          application={this.state.job}
          handleCloseEditModal={this.handleCloseEditModal.bind(this)}
          deleteApplication={this.deleteTheApplication.bind(this)}
        />
      );
    }

    return (
      <div>
        <div className="d-flex justify-content-center my-5">
          <input
            type="text"
            id="searchText"
            className="form-control px-4 py-3 w-50"
            placeholder="Keyword"
            aria-label="Username"
            aria-describedby="basic-addon1"
            value={this.state.searchText}
            onChange={this.handleChange.bind(this)}
            style={{ fontSize: 18, marginRight: 20 }}
          />
          <button
            type="button"
            className="px-4 py-3 custom-btn"
            onClick={this.search.bind(this)}
            disabled={this.state.searching}
          >
            Search
          </button>
        </div>
        {!this.state.searching && this.state.rows.length ? (
          <table
            className="table my-4"
            style={{
              boxShadow: "0px 5px 12px 0px rgba(0,0,0,0.1)",
              marginTop: 30,
              marginLeft: "10%",
              width: "95%",
              paddingRight: 10,
            }}
          >
            <thead>
              <tr>
                {columns.map((column) => {
                  return (
                    <th
                      className="p-3"
                      key={column.id + "_th"}
                      style={{
                        fontSize: 18,
                        fontWeight: "500",
                        backgroundColor: "#2a6e85",
                        color: "#fff",
                      }}
                    >
                      {column.label}
                    </th>
                  );
                })}
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => {
                return (
                  <tr key={row.id}>
                    {columns.map((column) => {
                      const value = row[column.id];
                      if (column.id !== "func") {
                        return (
                          <td className="p-3" key={column.id}>
                            {value}
                          </td>
                        );
                      } else {
                        <button
                          type="button"
                          className="add-btn px-3 py-2"
                          // onClick={this.showEditModal.bind(this, row)}
                          onClick={this.handleShowJobDesc.bind(this, row)}
                          // style={{
                          //   backgroundColor: "#296E85",
                          //   border: "none",
                          // }}
                        >
                          Details
                        </button>;
                        const addButton = this.state.addedList.includes(
                          row.id
                        ) ? (
                          <button
                            type="button"
                            className="btn btn-outline-secondary"
                            onClick={this.removeFromWaitlist.bind(this, row)}
                          >
                            Added
                          </button>
                        ) : (
                          <button
                            type="button"
                            className="add-btn px-3 py-2"
                            // onClick={this.showEditModal.bind(this, row)}
                            onClick={this.handleShowJobDesc.bind(this, row)}
                            // style={{
                            //   backgroundColor: "#296E85",
                            //   border: "none",
                            // }}
                          >
                            Details
                          </button>
                        );
                        return (
                          <td key={row.id + "_func"} className="p-2">
                            {/* <div className="container"> */}
                            <div className="d-flex justify-content-evenly">
                              {addButton}
                              {/* <button
                                type="button"
                                // style={{
                                //   backgroundColor: "#e54b4b",
                                //   border: "none",
                                //   color: "#fff",
                                //   borderRad
                                // }}
                                className="delete-btn px-3 py-2"
                                onClick={this.deleteTheApplication.bind(
                                  this,
                                  row.id
                                )}
                                style={{
                                  marginLeft:'2px'
                                }}
                              >
                                {" "}
                                Delete{" "}
                              </button> */}
                            </div>
                            {/* <div className="row">
                                <div className="col-md-4">{addButton}</div>
                                &nbsp;&nbsp;
                                <div className="col-md-2">
                                  <button
                                    type="button"
                                    style={{
                                      backgroundColor: "#e54b4b",
                                      border: "none",
                                    }}
                                    className="btn btn-secondary"
                                    onClick={this.deleteTheApplication.bind(
                                      this,
                                      row.id
                                    )}
                                  >
                                    {" "}
                                    Delete{" "}
                                  </button>
                                </div>
                              </div> */}
                            {/* </div> */}
                          </td>
                        );
                      }
                    })}
                  </tr>
                );
              })}
            </tbody>
          </table>
        ) : null}
        {this.state.searching && (
          <div className="d-flex justify-content-center my-5">
            <Spinner animation="border" style={{ fontSize: 15 }} />
          </div>
        )}
        {this.state.showJobDesc && (
          <JobDescription
            selectedJob={this.state.selectedJob}
            setState={this.handleShowJobDesc.bind(this)}
          />
        )}
        {applicationModal}
      </div>
    );
  }
}

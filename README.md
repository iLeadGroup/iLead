# iLead
This project aims to identify, investigate and measure emergent leadership in online software development communities.

## Leadership 
Leadership is a concept in public management, which involves a process whereby intentional influence is exerted over other people to guide, structure, and facilitate activities andrelationships in a group or organization.

In most forms of leadership, there are leaders and followers. In issue discussions on many open source projects, we found that many of the comments have the nature of leadership, but there are differences in that the developers who published the leadership comments are not appointed leaders. This type of leadership is emergent leadership that we are studying.

### Emergent Leadership
Emergent leadership occurs when a group member is not appointed or elected as leader, but rather that person steps up as the leader over time within group interactions. It also empowers team members to make decisions outside the traditional structure of a business organization.

## Motivation
In general, the OSS community is an ecosystem composed of a group of closely related OSS projects that draw expertise and contributions from a group of developers. OSS developers often play roles based on personal interests, rather than having tasks assigned to them by others. This freedom of function/responsibility, while very different from tradition, will certainly facilitate the open innovation that drives OSS success.

As an example of such an open contribution, a developer may only invest in a specific OSS project, and he/she may choose to submit a code contribution or participate in a discussion of the issue. However, we find that GitHub is easy to get rich information about developer contribution in code, but it is not an effective way to divide developer performance in issue discussions.

## Aims
Specifically, we are interested in exploring data-driven evidences to understand the following questions: What constitutes leadership in a virtual environment (leadership can be a temporary positioning rather than a stable role)? 2.	How do people emerge as leaders in an issue/task/community? What role does diversity play in virtual teams? Does the virtual software development environment eliminate any racial/gender biases or does it perpetuate them? 

## Methodology: 
- establish/refine codebook for identifying leadership practices based on manual labelling
- manual label to establish ground truth
- train classifiers
- evaluate performance of initial classifier
- impact analysis

We are currently focusing on the automatic identification of leadership, and we plan to explore this further in our future work.

## Running
> cd code
> python pattern_matcher.py

## Files
The details of folders:

* code

> The defined heuristic linguistic patterns and leadership identification program.

* prediction

> The prediction results.

* Leadership.xlsx

> The defined leadership.

* comments

> The list of comments we use.

* issues

> The list of issues we use.

* survey

> The questionnaires and responses.

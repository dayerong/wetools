#!/usr/bin/env python
# -*- coding: utf-8 -*-

import jenkins
from config.conf import jenkins_config


class JenkinsOperation(object):
    def __init__(self):
        self.jenkins_url = jenkins_config['jenkins_url']
        self.user = jenkins_config['user']
        self.password = jenkins_config['password']

    def buildjob(self, job_name, param=None):
        op = jenkins.Jenkins(self.jenkins_url, self.user, self.password)
        rs = op.build_job(job_name, param)
        return rs
        # last_build_number = op.get_job_info(job_name)['lastCompletedBuild']['number']
        # build_info = op.get_build_info(job_name, last_build_number)
        # print(build_info)

    def getjobs(self):
        op = jenkins.Jenkins(self.jenkins_url, self.user, self.password)
        jobs = op.get_jobs()
        return jobs

    def getalljobs(self):
        jobs = self.getjobs()
        job_list = {}
        for i in jobs:
            job_type = i['_class']
            if 'WorkflowMultiBranchProject' in job_type:
                job_name = i['name']
                sub_job_name = [i['name'] for i in i['jobs']]
                # job_list.append({job_name: sub_job_name})
                job_list[job_name] = sub_job_name
            elif 'FreeStyleProject' in job_type:
                job_name = i['name']
                sub_job_name = ''
                # job_list.append({job_name: sub_job_name})
                job_list[job_name] = sub_job_name
        return job_list

    def getjobinfo(self, name):
        op = jenkins.Jenkins(self.jenkins_url, self.user, self.password)
        info = op.get_job_info(name)
        return info

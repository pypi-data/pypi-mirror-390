from restclients_core import models


class Major(models.Model):
    major_abbr = models.CharField(max_length=32)
    program_code = models.CharField(max_length=128)
    academic_qtr_key_id = models.IntegerField()
    major_pathway = models.IntegerField()
    display_name = models.CharField(max_length=255)
    college = models.CharField(max_length=255)
    division = models.CharField(max_length=255)
    dtx = models.CharField(max_length=255)
    assigned_count = models.IntegerField()
    assigned_resident = models.IntegerField(null=True)
    assigned_nonresident = models.IntegerField(null=True)
    assigned_international = models.IntegerField(null=True)
    assigned_freshman = models.IntegerField(null=True)
    assigned_transfer = models.IntegerField(null=True)
    assigned_postbac = models.IntegerField(null=True)


class Cohort(models.Model):
    academic_qtr_id = models.IntegerField()
    cohort_number = models.IntegerField()
    cohort_description = models.TextField()
    cohort_residency = models.CharField(max_length=255)
    admit_decision = models.CharField(max_length=255)
    protected_group = models.BooleanField()
    active_cohort = models.BooleanField()
    assigned_count = models.IntegerField()
    assigned_freshman = models.IntegerField(null=True)
    assigned_transfer = models.IntegerField(null=True)
    assigned_postbac = models.IntegerField(null=True)


class Decision(models.Model):
    decision_name = models.CharField(max_length=255)
    decision_id = models.CharField(max_length=128)
    assigned_count1 = models.IntegerField()
    assigned_count2 = models.IntegerField()


class Quarter(models.Model):
    id = models.IntegerField()
    begin = models.DateTimeField()
    end = models.DateTimeField()
    active_ind = models.CharField(max_length=32)
    appl_yr = models.CharField(max_length=4)
    appl_qtr = models.CharField(max_length=1)
    is_current = models.BooleanField()


class Activity(models.Model):
    assignment_date = models.DateTimeField()
    comment = models.TextField()
    user = models.CharField(max_length=12)
    assignment_type = models.TextField()
    cohort_number = models.IntegerField()
    major_abbr = models.CharField(max_length=32)
    major_program_code = models.CharField(max_length=32)
    total_submitted = models.IntegerField()
    total_assigned = models.IntegerField()
    application_type = models.CharField(max_length=128)


class Application(models.Model):
    adsel_id = models.IntegerField()
    application_number = models.IntegerField()
    system_key = models.IntegerField()
    campus = models.IntegerField()
    quarter_id = models.IntegerField()
    assigned_cohort = models.IntegerField()
    assigned_major = models.CharField(max_length=32)
    major_program_code = models.CharField(max_length=255)
    application_type = models.CharField(max_length=255)

    def json_data(self):
        return {'admissionSelectionId': int(self.adsel_id),
                'applicationNbr': self.application_number,
                'systemKey': int(self.system_key),
                'applicationType': self.application_type}

    def major_assign_json_data(self):
        return {'AdmissionSelectionId': int(self.adsel_id),
                'ApplicationNbr': self.application_number,
                'SystemKey': int(self.system_key)}


class PurpleGoldApplication(Application):
    award_amount = models.IntegerField()

    def json_data(self):
        return {'AdmissionSelectionId': int(self.adsel_id),
                'AwardAmount': self.award_amount}


class DepartmentalDecisionApplication(Application):
    decision_id = models.IntegerField()

    def json_data(self):
        return {'admissionSelectionId': int(self.adsel_id),
                'departmentalDecisionId': self.decision_id}


class Assignment(models.Model):
    assignment_type = models.CharField()
    quarter = models.IntegerField()
    campus = models.IntegerField()
    comments = models.TextField()
    user = models.CharField(max_length=12)
    applicants = []
    workspace_id = models.IntegerField()


class CohortAssignment(Assignment):
    cohort_number = models.IntegerField()
    override_previous = models.BooleanField()
    override_protected = models.BooleanField()

    def json_data(self):
        applicant_json = []
        for application in self.applicants:
            applicant_json.append(application.json_data())
        return {'applicants': applicant_json,
                'cohortNbr': int(self.cohort_number),
                'overridePreviousCohort': self.override_previous,
                'overridePreviousProtectedCohort': self.override_protected,
                'assignmentDetail': {'assignmentType': self.assignment_type,
                                     'academicQtrKeyId': self.quarter,
                                     'campus': int(self.campus),
                                     'comments': self.comments,
                                     'decisionImportUser': self.user,
                                     'workspaceId': self.workspace_id}
                }


class MajorAssignment(Assignment):
    major_code = models.CharField()

    def json_data(self):
        applicant_json = []
        for application in self.applicants:
            applicant_json.append(application.major_assign_json_data())
        return {'Applicants': applicant_json,
                'MajorProgramCode': self.major_code,
                'AssignmentDetail': {
                    'AssignmentCategory': "Major",
                    'AssignmentType': self.assignment_type,
                    'AcademicQtrKeyId': self.quarter,
                    'Campus': int(self.campus),
                    'Comments': self.comments,
                    'DecisionImportUser': self.user,
                    'WorkspaceId': self.workspace_id
                }
                }


class PurpleGoldAssignment(Assignment):
    def json_data(self):
        applicant_json = []
        for application in self.applicants:
            applicant_json.append(application.json_data())
        return {'Applicants': applicant_json,
                'AssignmentDetail': {
                    "AssignmentCategory": "PuGo",
                    'AssignmentType': "manual",
                    'AcademicQtrKeyId': self.quarter,
                    'Comments': self.comments,
                    'Campus': int(self.campus),
                    'DecisionImportUser': self.user,
                    'WorkspaceId': self.workspace_id}
                }


class DecisionAssignment(Assignment):
    decision = models.CharField()
    decision_number = models.IntegerField()

    def json_data(self):
        applicant_json = []
        for application in self.applicants:
            applicant_json.append(application.json_data())
        return {'applicants': applicant_json,
                'assignmentDetail': {'assignmentType': self.assignment_type,
                                     'assignmentCategory':
                                         "DepartmentalDecision",
                                     'academicQtrKeyId': self.quarter,
                                     'campus': int(self.campus),
                                     'comments': self.comments,
                                     'decisionImportUser': self.user,
                                     'decisionNumber': self.decision_number,
                                     'workspaceId': self.workspace_id}
                }


class AdminMajor(models.Model):
    major_id = models.IntegerField()
    major_abbr = models.CharField(max_length=32)
    begin_academic_qtr_key_id = models.IntegerField()
    end_academic_qtr_key_id = models.IntegerField()
    major_pathway = models.IntegerField()
    display_name = models.CharField(max_length=255)
    college = models.CharField(max_length=255)
    division = models.CharField(max_length=255)
    dtx = models.CharField(max_length=255)
    dtx_desc = models.CharField(max_length=255)
    directToMajorInd = models.BooleanField()
    directToCollegeInd = models.IntegerField()
    majorDegreeLevel = models.IntegerField()
    majorDegreeType = models.IntegerField()
    assignedMajorAbbr = models.CharField(max_length=255)
    assignedMajorDegreeLevel = models.IntegerField()
    assignedMajorDegreeType = models.IntegerField()
    majorAssignedName = models.CharField(max_length=255)
    assignedMajorPathway = models.IntegerField()

    def json_data(self):
        return {
            "id": self.major_id,
            "majorAbbr": self.major_abbr,
            "beginAcademicQtrKeyId": self.begin_academic_qtr_key_id,
            "endAcademicQtrKeyId": self.end_academic_qtr_key_id,
            "majorPathway": self.major_pathway,
            "displayName": self.display_name,
            "collegeCode": self.college,
            "collegeDivision": self.division,
            "directToXType": self.dtx,
            "directToXDesc": self.dtx_desc,
            "directToMajorInd": self.directToMajorInd,
            "directToCollegeInd": self.directToCollegeInd,
            "majorDegreeLevel": self.majorDegreeLevel,
            "majorDegreeType": self.majorDegreeType,
            "assignedMajorAbbr": self.assignedMajorAbbr,
            "assignedMajorDegreeLevel": self.assignedMajorDegreeLevel,
            "assignedMajorDegreeType": self.assignedMajorDegreeType,
            "majorAssignedName": self.majorAssignedName,
            "assignedMajorPathway": self.assignedMajorPathway
        }


class AdminCohort(models.Model):
    academic_qtr_id = models.IntegerField()
    cohort_number = models.IntegerField()
    cohort_description = models.TextField()
    cohort_residency = models.CharField(max_length=255)
    cohort_campus = models.IntegerField()
    cohort_application_type = models.IntegerField()
    admit_decision = models.CharField(max_length=255)
    protected_group = models.BooleanField()
    enforce_exceptions = models.BooleanField()
    active_cohort = models.BooleanField()
    record_updated = models.DateTimeField()
    record_update_user = models.CharField(max_length=255)

    def json_data(self):
        return {
            "academicQtrKeyId": self.academic_qtr_id,
            "cohortNbr": self.cohort_number,
            "cohortDescription": self.cohort_description,
            "cohortResidency": self.cohort_residency,
            "cohortCampus": self.cohort_campus,
            "cohortApplicationType": self.cohort_application_type,
            "admitDecision": self.admit_decision,
            "protectedGroupInd": self.protected_group,
            "enforceExceptionsInd": self.enforce_exceptions,
            "activeCohortInd": self.active_cohort,
            "recordUpdateDateTime": self.record_updated,
            "recordUpdateUser": self.record_update_user
        }


class Workspace(models.Model):
    academic_qtr_id = models.IntegerField()
    workspace_id = models.IntegerField()
    workspace_name = models.CharField(max_length=255)
    owner_alias = models.CharField(max_length=255)
    source_workspace_id = models.IntegerField()
    workspace_status_id = models.IntegerField()
    workspace_status_desc = models.CharField(max_length=255)

    def json_data(self):
        return {
            "academicQtrKeyId": self.academic_qtr_id,
            "workspaceId": self.workspace_id,
            "workspaceName": self.workspace_name,
            "ownerAlias": self.owner_alias,
            "sourceWorkspaceId": self.source_workspace_id,
            "workspaceStatusId": self.workspace_status_id,
            "workspaceStatusDesc": self.workspace_status_desc
        }


class Conflict(models.Model):
    source_ws = models.IntegerField()
    source_ws_name = models.CharField(max_length=255)
    source_assigned_count = models.IntegerField()
    destination_ws = models.IntegerField()
    destination_ws_name = models.CharField(max_length=255)
    destination_assigned_count = models.IntegerField()
    conflict_status = models.BooleanField()

    def init_from_json(self, json_data):
        self.source_ws = json_data.get('source_ws')
        self.source_ws_name = json_data.get('source_ws_name')
        self.destination_ws = json_data.get('destination_ws')
        self.destination_ws_name = json_data.get('destination_ws_name')
        self.conflict_status = json_data.get('conflictStatus')
        self.source_assigned_count = (
            json_data.get('source_ws_applicationCount'))
        self.destination_assigned_count = json_data.get(
            'dest_ws_applicationCount')

    @classmethod
    def conflicts_from_response(cls, json_list):
        return [cls().init_from_json(json_data) for json_data in json_list]


class CohortConflict(Conflict):
    source_cohort = models.IntegerField()

    def init_from_json(self, json_data):
        super().init_from_json(json_data)
        self.source_cohort = json_data.get('sourceAssignedCohort')
        return self


class MajorConflict(Conflict):
    source_major = models.CharField(max_length=64)

    def init_from_json(self, json_data):
        super().init_from_json(json_data)
        self.source_major = json_data.get('majorCode')
        return self


class Merge(models.Model):
    from_ws_id = models.IntegerField()
    to_ws_id = models.IntegerField()
    comments = models.TextField()
    user = models.CharField(max_length=64)

    def to_json(self):
        return {
            'fromWorkspaceId': self.from_ws_id,
            'toWorkspaceId': self.to_ws_id,
            'comments': self.comments,
            'decisionImportUser': self.user
        }


class CohortMerge(Merge):
    cohort_number = models.IntegerField()

    def to_json(self):
        data = super().to_json()
        data['cohortNbr'] = self.cohort_number
        return data


class MajorMerge(Merge):
    major_code = models.CharField(max_length=32)

    def to_json(self):
        data = super().to_json()
        data['majorProgramCode'] = self.major_code
        return data

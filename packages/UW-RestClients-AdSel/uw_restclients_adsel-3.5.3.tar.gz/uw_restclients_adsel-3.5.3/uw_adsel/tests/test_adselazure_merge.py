from unittest import TestCase
from uw_adsel import AdSelAzureMerge
from uw_adsel.models import CohortMerge, MajorMerge


class AdselTest(TestCase):
    adsel = AdSelAzureMerge()

    # Due to mocking limits from/to IDs aren't tested

    def test_cohort_conflict(self):
        conflicts = self.adsel.check_conflict_cohort(1, 2)
        self.assertEqual(len(conflicts), 10)
        self.assertEqual(conflicts[0].source_ws, 1)
        self.assertEqual(conflicts[0].source_ws_name, 'WS One')
        self.assertEqual(conflicts[0].destination_ws, 2)
        self.assertEqual(conflicts[0].destination_ws_name, 'WS Two')
        self.assertEqual(conflicts[0].source_cohort, 1)
        self.assertEqual(conflicts[0].conflict_status, True)
        self.assertEqual(conflicts[1].conflict_status, False)
        self.assertEqual(conflicts[0].source_assigned_count, 150)
        self.assertEqual(conflicts[0].destination_assigned_count, 200)

    def test_cohort_conflict_details(self):
        details = self.adsel.get_conflict_details_cohort(1, 2)
        detail_lines = details.split('\n')
        self.assertEqual(len(detail_lines), 9)

    def test_cohort_conflict_details_csv(self):
        details = self.adsel.get_conflict_details_cohort(1, 2)
        detail_lines = details.split('\n')
        expected_headers = """lastSchoolName,source_ws,lastSchoolCode,
        source_ws_name,highSchoolCity,highSchoolState,destination_ws,highSchoo
        lFRLPct,destination_ws_name,lowFamilyIncomeInd,sdbSrcSystemKey,firstGe
        nerationInd,applicationType,athleteCode,admissionsSelectionId,requeste
        dMajor1Name,academicQtrKeyId,requestedMajor1College,studentName,request
        edMajor2Name,applicationNbr,requestedMajor2College,gender,permanentStat
        e,underrepresentedMinorityDesc,reasonCode,ipedsRaceEthnicityCategory,s
        dbCohort,residentGroup,residentCategory,sdbApplicationStatus,anyAdmiss
        ionsRecommendation,sdbEmail,anyAcademic,anyPQA,highSchoolGPA,mathLeve
        lCode,highestConcordedSATTotal,highestConcordedSATReadingWriting,hig
        hestConcordedSATMath,sourceAssignedCohort,destinationAssignedCohort
        ,assignedCohortConflictStatus,assignedMajor1Name,adSelAssignedMajorNa
        me,adSelAssignedMajorProgramCode"""
        self.assertEqual(len(detail_lines), 9)
        self.assertIn("Bill Student", detail_lines[1])

    def test_major_conflict(self):
        conflicts = self.adsel.check_conflict_major(1, 2)
        self.assertEqual(len(conflicts), 10)
        self.assertEqual(conflicts[0].source_ws, 1)
        self.assertEqual(conflicts[0].source_ws_name, 'WS One')
        self.assertEqual(conflicts[0].destination_ws, 2)
        self.assertEqual(conflicts[0].destination_ws_name, 'WS Two')
        self.assertEqual(conflicts[0].source_major, '0_C SCI_00_1_5')
        self.assertEqual(conflicts[0].conflict_status, True)
        self.assertEqual(conflicts[1].conflict_status, False)
        self.assertEqual(conflicts[0].source_assigned_count, 40)
        self.assertEqual(conflicts[0].destination_assigned_count, 50)

    def test_major_merge(self):
        mm = MajorMerge(
            from_ws_id=1,
            to_ws_id=2,
            comments='Test merge 1>2',
            major_code='0_BIOL_1',
            user='testuser'
        )
        self.assertDictEqual(
            mm.to_json(),
            {
                'fromWorkspaceId': 1,
                'toWorkspaceId': 2,
                'comments': 'Test merge 1>2',
                'majorProgramCode': '0_BIOL_1',
                'decisionImportUser': 'testuser'
            }
        )
        response = self.adsel.merge_major(mm)
        self.assertEqual(response["string_response"], "")

    def test_cohort_merge(self):
        cm = CohortMerge(
            from_ws_id=1,
            to_ws_id=2,
            comments='Test merge 1>2',
            cohort_number=1,
            user='testuser'
        )
        self.assertDictEqual(
            cm.to_json(),
            {
                'fromWorkspaceId': 1,
                'toWorkspaceId': 2,
                'comments': 'Test merge 1>2',
                'cohortNbr': 1,
                'decisionImportUser': 'testuser'
            }
        )

        response = self.adsel.merge_cohort(cm)
        self.assertEqual(response["string_response"], "")

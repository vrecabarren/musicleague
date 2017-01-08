import logging

from musicleague import app
from musicleague.models import League
from musicleague.models import Submission
from musicleague.models import SubmissionPeriod
from musicleague.routes.decorators import admin_required
from musicleague.routes.decorators import login_required


CLEAN_SUBMISSION_PERIODS_URL = '/admin/clean/submission_periods/'
CLEAN_SUBMISSIONS_URL = '/admin/clean/submissions/'


@app.route(CLEAN_SUBMISSION_PERIODS_URL, methods=['GET'])
@login_required
@admin_required
def clean_submission_periods():
    valid_periods = set()

    for league in League.objects().all():
        valid_periods.update([sp.id for sp in league.submission_periods])

    for sp in SubmissionPeriod.objects().all():
        if sp.id not in valid_periods:
            logging.warning('Removing Submission Period %s', sp.id)
            sp.delete()


@app.route(CLEAN_SUBMISSIONS_URL, methods=['GET'])
@login_required
@admin_required
def clean_submissions():
    valid_submissions = set()

    for sp in SubmissionPeriod.objects().all():
        valid_submissions.update([sub.id for sub in sp.submissions])

    for sub in Submission.objects().all():
        if sub.id not in valid_submissions:
            logging.warning('Removing Submission %s', sub.id)
            sub.delete()

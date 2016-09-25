import logging

from flask import g
from flask import redirect
from flask import request

from feedback import app
from feedback.models import League
from feedback.models import Submission
from feedback.models import SubmissionPeriod
from feedback.routes.decorators import login_required


CLEAN_SUBMISSION_PERIODS_URL = '/admin/clean/submission_periods/'
CLEAN_SUBMISSIONS_URL = '/admin/clean/submissions/'


@app.route(CLEAN_SUBMISSION_PERIODS_URL, methods=['GET'])
@login_required
def clean_submission_periods():
    if g.user.email == 'nathandanielcoleman@gmail.com':
        valid_periods = set()

        for league in League.objects().all():
            valid_periods.update([sp.id for sp in league.submission_periods])

        for sp in SubmissionPeriod.objects().all():
            if sp.id not in valid_periods:
                logging.warning('Removing Submission Period %s', sp.id)
                sp.delete()

    return redirect(request.referrer)


@app.route(CLEAN_SUBMISSIONS_URL, methods=['GET'])
@login_required
def clean_submissions():
    if g.user.email == 'nathandanielcoleman@gmail.com':
        valid_submissions = set()

        for sp in SubmissionPeriod.objects().all():
            valid_submissions.update([sub.id for sub in sp.submissions])

        for sub in Submission.objects().all():
            if sub.id not in valid_submissions:
                logging.warning('Removing Submission %s', sub.id)

    return redirect(request.referrer)

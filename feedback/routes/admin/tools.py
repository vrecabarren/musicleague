import logging

from flask import g
from flask import redirect
from flask import request

from feedback import app
from feedback.models import League
from feedback.models import SubmissionPeriod
from feedback.routes.decorators import login_required


CLEAN_SUBMISSION_PERIODS_URL = '/admin/clean/submission_period/'


@app.route(CLEAN_SUBMISSION_PERIODS_URL, methods=['GET'])
@login_required
def clean_submission_periods():
    if g.user.email == 'nathandanielcoleman@gmail.com':
        valid_periods = set()

        for league in League.objects().all():
            valid_periods.update([sp.id for sp in league.submission_periods])

        for sp in SubmissionPeriod.objects().all():
            if sp.id not in valid_periods:
                logging.warning('Removing %s', sp.id)
                sp.delete()

    return redirect(request.referrer)

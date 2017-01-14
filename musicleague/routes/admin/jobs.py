from flask import redirect
from flask import request

from musicleague import app
from musicleague import scheduler
from musicleague.notify.flash import flash_error
from musicleague.notify.flash import flash_success
from musicleague.routes.decorators import admin_required
from musicleague.routes.decorators import login_required


CANCEL_JOB_URL = '/admin/jobs/<job_id>/cancel/'


@app.route(CANCEL_JOB_URL)
@login_required
@admin_required
def cancel_job(job_id):
    if not job_id or job_id not in scheduler:
        flash_error('Job ID <strong>{}</strong> not found.'.format(job_id))
        return

    scheduler.cancel(job_id)
    flash_success('Job ID <strong>{}</strong> cancelled.'.format(job_id))
    return redirect(request.referrer)

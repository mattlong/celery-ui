def run_task(data):
    from werkzeug.utils import import_string

    args = []

    for k, v in data.items():
        if k == '_task_name':
            task_name = v
        else:
            args.append(v)

    task_class = import_string(task_name)
    r = task_class.delay(*args)

    response = {'task': task_name, 'id': r.id}
    return response


def get_task_result(task_id):
    from celery.result import AsyncResult

    r = AsyncResult(task_id)
    response = {'id': task_id, 'status': r.status, 'ready': r.ready()}
    if response['ready']:
        response['result'] = r.result
    return response

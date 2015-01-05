def run_task(data):
    from werkzeug.utils import import_string
    from celery_ui.arguments import parse_value, prepare_arguments

    try:
        all_args = {}
        for k, v in data.items():
            if k == '_task_name':
                task_name = v

            else:
                v = parse_value(v)
                all_args[k] = v

        task_class = import_string(task_name)
        args, kwargs = prepare_arguments(task_class.run, all_args)

        r = task_class.apply_async(args=args, kwargs=kwargs)
        response = {'task': task_name, 'id': r.id}
        return response
    except Exception, ex:
        return {'error': str(ex)}


def get_task_result(task_id):
    from celery.result import AsyncResult

    r = AsyncResult(task_id)
    response = {'id': task_id, 'status': r.status, 'ready': r.ready()}
    if r.failed():
        response['error'] = r.traceback
    else:
        response['result'] = r.result

    return response

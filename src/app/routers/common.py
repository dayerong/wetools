import json

from fastapi import APIRouter, Request
from api.sendWxMsg import sendPushMsg, sendMergeMsg
from config.conf import git_hooks_config
from common.logs import Log

router = APIRouter()


# Gitlab Webhooks
@router.post("/v1/git/webhooks")
async def hooks(request: Request):
    log = Log()
    json_param = await request.json()
    header_token = request.headers.get('X-Gitlab-Token')
    secret_token = git_hooks_config['secret_token']
    userid = git_hooks_config['userid']
    event_name = json_param['object_kind']
    if header_token == secret_token:
        try:
            if event_name == 'push':
                push_info = {
                    'project': json_param['project']['name'],
                    'branch': json_param['project']['default_branch'],
                    'event_name': event_name,
                    'commit_id': json_param['commits'][0]['id'],
                    'commit_title': json_param['commits'][0]['title'],
                    'commit_timestamp': json_param['commits'][0]['timestamp'][:-6].replace('T', ' '),
                    'author_name': json_param['commits'][0]['author']['name'],
                    'author_email': json_param['commits'][0]['author']['email'],
                }
                sendPushMsg(userid, push_info)

            elif event_name == 'merge_request':
                merge_info = {
                    'project': json_param['project']['name'],
                    'source_branch': json_param['object_attributes']['source_branch'],
                    'target_branch': json_param['object_attributes']['target_branch'],
                    'event_name': event_name,
                    'merge_commit_sha': json_param['object_attributes']['merge_commit_sha'],
                    'commit_title': json_param['object_attributes']['title'],
                    'commit_timestamp': json_param['object_attributes']['created_at'][:-6].replace('T', ' '),
                    'author_name': json_param['object_attributes']['last_commit']['author']['name'],
                    'author_email': json_param['object_attributes']['last_commit']['author']['email'],
                    'assignees': json_param['assignees'][0]['name'],
                }
                sendMergeMsg(userid, merge_info)
        except Exception as e:
            print(e)
            log.info('git_webhooks', 'error:{0}'.format(e))

    else:
        print('authentication failure')
        log.info('git_webhooks', 'authentication failure')

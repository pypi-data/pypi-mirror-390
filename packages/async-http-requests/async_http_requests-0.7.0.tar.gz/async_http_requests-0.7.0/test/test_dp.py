from src.AsyncRequests import AsyncHTTP, RequestType, RequestObject
from time import perf_counter
import requests
import json
import pandas as pd



BRANCH = "free-thread"
N_REQUESTS = 3000
API = f"https://one-api.miodottore.it/api/patients"

def get_profile_info(token: str):
    header = {"authorization": token}
    r = requests.get("https://docplanner.miodottore.it/api/profile", headers = header)
    return json.dumps(r.json())

def n_patients(token):

    n_pat = 0

    header = {"authorization": token}
    # endpoint = 'https://one-api.miodottore.it/api/patients/pagedList'
    endpoint = 'https://docplanner.miodottore.it/api/patients/pagedList'
    req = requests.post(endpoint, headers=header, json={
        'createdFrom': None,
        'filter': None,
        'hasEmail': None,
        'hasPhone': None,
        'isOwner': 'false',
        'isPublic': None,
        'marketingConsentAccepted': None,
        'orderBy': 'firstname',
        'pageNumber': 1,
        'pageSize': 100_000_000
        }).json()

    patids_df = pd.json_normalize(req['page'])
    if len(patids_df) > 0:
        n_pat += len(patids_df)
        print(f"Number of Patients: {len(patids_df)}")
        # return json.dumps({"n_patients": len(patids_df)}), patids_df
    # else:
    req = requests.post(endpoint, headers=header, json={
        'createdFrom': None,
        'filter': None,
        'hasEmail': None,
        'hasPhone': None,
        'isOwner': None,
        'isPublic': None,
        'marketingConsentAccepted': None,
        'orderBy': 'firstname',
        'pageNumber': 1,
        'pageSize': 100_000_000
        }).json()
    patids_df_no_owner = pd.json_normalize(req['page'])
    if (len(patids_df_no_owner))>0:
        n_pat += len(patids_df_no_owner)
    if (len(patids_df)) >0 and len(patids_df_no_owner)>0:
        patids_df = pd.concat([patids_df, patids_df_no_owner])
    if len(patids_df_no_owner) >0 and len(patids_df)==0:
        patids_df = patids_df_no_owner
    print(f"Number of Patients: {len(patids_df)}")
    return json.dumps({"n_patients": len(patids_df)}), patids_df



if __name__ == '__main__':
    token = "bearer OGRlZjY1MmI4NDc5Njc2OTI4N2NhZWI5ZGMyYjZmN2EzNWRiZGFiNDMxYmM2OTg0ZTcwMWYzNjliZTIyZjk2NQ"
    headers = {"authorization": token}
    profile_info = get_profile_info(token)
    print(profile_info)
    _, df_pat = n_patients(token)
    url = [RequestObject(url = f"{ API }/{pat_id}") for pat_id in df_pat['id'].to_list()]

    start = perf_counter()
    a = AsyncHTTP(url = url)
    a.async_request(
        request_type=RequestType.GET,
        multithreaded=True,
        callback=lambda x : x.json(),
        max_retries=5,
        headers = headers,
    )

    end = perf_counter()

    print(a.response)
    print(len( a.response ))
    print(len( a.error_response ))
    print(pd.json_normalize(a.response))

    print(BRANCH)
    print(f"Time elapsed for {N_REQUESTS}: {end-start}")

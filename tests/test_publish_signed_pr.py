"""Signing and concurrency regressions for generated-file publishing."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import unittest
from unittest import mock

spec=importlib.util.spec_from_file_location("publisher",Path(__file__).resolve().parents[1]/".github/scripts/publish_signed_pr.py")
publisher=importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)
OID="f"*40
BASE="a"*40
class PublisherTest(unittest.TestCase):
    def execute(self,verification=None,parents=None,old=None,lease_error=False,event="workflow_dispatch",default="main"):
        calls=[]
        def fake(*args,stdin=None):
            calls.append((args,json.loads(stdin) if stdin else None))
            if args[:3]==("gh","pr","create"): return "https://example.invalid/pr/1"
            if args[:3]==("gh","pr","list"): return "[]"
            endpoint=args[2]
            if endpoint=="repos/o/r": return json.dumps({"node_id":"REPO","default_branch":default})
            if "matching-refs" in endpoint:
                return json.dumps([] if old is None else [{"ref":"refs/heads/automation/x","object":{"sha":old}}])
            if endpoint=="graphql":
                payload=json.loads(stdin)
                if "UpdateRefsInput" in payload["query"]:
                    if lease_error: return json.dumps({"errors":[{"message":"stale beforeOid"}]})
                    return '{"data":{"updateRefs":{"clientMutationId":null}}}'
                return json.dumps({"data":{"createCommitOnBranch":{"commit":{"oid":OID,"url":"u"}}}})
            if endpoint.endswith("/commits/"+OID):
                return json.dumps({"sha":OID,"commit":{"verification":verification or {}},
                                   "parents":[{"sha":p} for p in (parents if parents is not None else [BASE])]})
            return "{}"
        with mock.patch.dict(os.environ,{"GITHUB_REPOSITORY":"o/r","GITHUB_EVENT_NAME":event}), \
             mock.patch.object(publisher,"changes",return_value=([{"path":"x","contents":"eA=="}],[])), \
             mock.patch.object(publisher,"run",side_effect=fake):
            result=publisher.main(["--branch","automation/x","--title","fix: x","--base","main","--base-sha",BASE,"x"])
        return result,calls
    def test_verified_signature_allows_pull_request(self):
        result,calls=self.execute({"verified":True,"reason":"valid"})
        self.assertEqual(result,0)
        self.assertTrue(any(a[:3]==("gh","pr","create") for a,_ in calls))
    def test_unsigned_invalid_missing_and_non_boolean_fail(self):
        for value in ({},{"verified":False,"reason":"unsigned"},{"verified":True,"reason":"unknown_key"},{"verified":1,"reason":"valid"}):
            with self.subTest(value=value), self.assertRaisesRegex(RuntimeError,"did not verify"):
                self.execute(value)
    def test_wrong_parent_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError,"did not verify"):
            self.execute({"verified":True,"reason":"valid"},parents=["b"*40])
    def test_force_update_is_bound_to_observed_head(self):
        result,calls=self.execute({"verified":True,"reason":"valid"},old="b"*40)
        payload=next(p for a,p in calls if p and "UpdateRefsInput" in p["query"])
        self.assertEqual(payload["variables"]["input"]["refUpdates"],[
            {"name":"refs/heads/automation/x","beforeOid":"b"*40,"afterOid":BASE,"force":True}])
    def test_stale_lease_aborts_before_signing(self):
        with self.assertRaisesRegex(RuntimeError,"refused"):
            self.execute({"verified":True,"reason":"valid"},old="b"*40,lease_error=True)
    def test_pull_request_target_and_default_branch_are_rejected(self):
        with self.assertRaisesRegex(RuntimeError,"pull_request_target"):
            self.execute(event="pull_request_target")
        with self.assertRaisesRegex(RuntimeError,"Default branch"):
            self.execute(default="automation/x")

if __name__=="__main__":
    unittest.main()

"""Security tests for meta_api: tokens stay out of URLs, paths cannot be injected."""
import importlib.util
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

SCRIPTS = Path(__file__).parents[1]
sys.path.insert(0, str(SCRIPTS / "lib"))
import meta_api  # noqa: E402

ENV = {"META_ACCESS_TOKEN": "tok-secret", "META_AD_ACCOUNT_ID": "12345"}


def load_script(name):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def response(payload, status=200, headers=None):
    resp = MagicMock(status_code=status, headers=headers or {})
    resp.json.return_value = payload
    return resp


class GraphUrlTests(unittest.TestCase):
    def test_builds_url_from_valid_segments(self):
        self.assertEqual(meta_api.graph_url("act_1", "ads"), f"{meta_api.BASE_URL}/act_1/ads")
        self.assertEqual(meta_api.graph_url("nike.store"), f"{meta_api.BASE_URL}/nike.store")

    def test_rejects_segments_that_change_path_or_query(self):
        for bad in ["me/adaccounts", "..", "x?access_token=1", "a#b", "a%2Fb", "", "evil.com/x"]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                meta_api.graph_url(bad)

    def test_is_graph_url_only_accepts_https_graph_host(self):
        self.assertTrue(meta_api.is_graph_url("https://graph.facebook.com/v23.0/act_1/insights?after=A"))
        for bad in ["http://graph.facebook.com/x", "https://graph.facebook.com.evil.test/x",
                    "https://evil.test/?u=https://graph.facebook.com", "https://graph.facebook.com:8443/x",
                    "https://user@evil.test/x", "https://graph.facebook.com:bad/x", None]:
            with self.subTest(bad=bad):
                self.assertFalse(meta_api.is_graph_url(bad))

    def test_ad_account_and_numeric_ids_are_validated(self):
        self.assertEqual(meta_api.normalize_ad_account("123"), "act_123")
        self.assertEqual(meta_api.normalize_ad_account("act_123"), "act_123")
        for bad in ["act_12/ads", "abc", "act_", "1 2"]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                meta_api.normalize_ad_account(bad)
        with self.assertRaises(ValueError):
            meta_api.numeric_id("1/../me")

    def test_rejects_malformed_api_version(self):
        with patch.dict(os.environ, {"META_API_VERSION": "v1/../../evil"}), self.assertRaises(RuntimeError):
            meta_api._api_version()


@patch.dict(os.environ, ENV)
class TokenHandlingTests(unittest.TestCase):
    def assert_token_only_in_header(self, call):
        self.assertEqual(call.kwargs["headers"], {"Authorization": "Bearer tok-secret"})
        self.assertNotIn("tok-secret", call.args[0])
        for key in ("params", "data"):
            self.assertNotIn("access_token", call.kwargs.get(key) or {})
        self.assertIn("timeout", call.kwargs)

    def test_create_ad_sends_token_in_header_with_timeout(self):
        with patch.object(meta_api.requests, "post", return_value=response({"id": "9"})) as post:
            self.assertEqual(meta_api.create_ad("555", "Ad", {"x": 1}), "9")
        self.assert_token_only_in_header(post.call_args)
        self.assertEqual(post.call_args.args[0], f"{meta_api.BASE_URL}/act_12345/ads")

    def test_create_ad_rejects_non_numeric_adset(self):
        with self.assertRaises(ValueError):
            meta_api.create_ad("1/../me", "Ad", {})

    def test_video_polling_validates_id_and_keeps_token_out_of_url(self):
        ready = {"status": {"processing_phase": {"status": "complete"}, "video_status": "ready"},
                 "picture": "https://cdn.test/p.jpg"}
        with patch.object(meta_api.time, "sleep"), \
                patch.object(meta_api.requests, "get", return_value=response(ready)) as get:
            self.assertEqual(meta_api.wait_for_video_processing("42"), "https://cdn.test/p.jpg")
        self.assert_token_only_in_header(get.call_args)
        with self.assertRaises(ValueError):
            meta_api.wait_for_video_processing("42/../me")


@patch.dict(os.environ, ENV)
class PaginationTests(unittest.TestCase):
    def test_pull_top_ads_stops_before_sending_token_to_foreign_host(self):
        mod = load_script("pull-top-ads")
        pages = [response({"data": [{"ad_id": "1"}], "paging": {"next": "https://evil.test/steal"}})]
        with patch.object(mod.requests, "get", side_effect=pages) as get:
            self.assertEqual(mod.get_ad_insights("123", "tok-secret", "maximum"), [{"ad_id": "1"}])
        self.assertEqual(get.call_count, 1)
        self.assertNotIn("tok-secret", str(get.call_args.kwargs.get("params")))

    def test_pull_competitor_ads_refuses_foreign_paging_and_caps_retries(self):
        mod = load_script("pull-competitor-ads")
        foreign = response({"data": [{"id": "a"}], "paging": {"next": "https://evil.test/x"}})
        with patch.object(mod.requests, "get", side_effect=[foreign]) as get:
            ads, err = mod.fetch_ads_archive("77", "tok-secret", ["US"], "d1", "d2", 10, "x", "ALL", "all")
        self.assertEqual((len(ads), get.call_count), (1, 1))
        self.assertIn("not a graph.facebook.com", err)

        busy = response({}, status=429, headers={"Retry-After": "99999"})
        with patch.object(mod.time, "sleep") as sleep, \
                patch.object(mod.requests, "get", return_value=busy) as get:
            ads, err = mod.fetch_ads_archive("77", "tok-secret", ["US"], "d1", "d2", 10, "x", "ALL", "all")
        self.assertEqual(get.call_count, mod.MAX_RETRIES + 1)
        self.assertTrue(all(c.args[0] <= mod.MAX_RETRY_WAIT for c in sleep.call_args_list))
        self.assertIn("Gave up", err)

    def test_resolve_page_id_rejects_path_injection_without_a_request(self):
        mod = load_script("pull-competitor-ads")
        with patch.object(mod.requests, "get") as get:
            self.assertIsNone(mod.resolve_page_id("me/adaccounts", "tok-secret"))
        get.assert_not_called()


if __name__ == "__main__":
    unittest.main()

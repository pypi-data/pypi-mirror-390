# pylint: disable=duplicate-code
"""
Unit tests for LeasewebClient
"""

import secrets
import unittest

import requests_mock

from certbot_dns_leaseweb.client import (
    LeasewebClient,
    LEASEWEB_DOMAIN_API_ENDPOINT,
    LEASEWEB_DOMAIN_API_LIST_LIMIT,
)


class LeasewebClientTestWithDomainOverride(unittest.TestCase):
    """Test suite for certbot_dns_leaseweb.client.LeasewebClient."""

    record_domain = "example.com"
    record_name = "_acme_challenge.example.com."
    record_content = ["test content"]
    record_ttl = 60

    override_record_domain = "override.net"
    override_record_name = "_acme_challenge.override.net"

    api_token = "notarealtoken"
    override_domain = "override.net"

    def setUp(self):
        self.client = LeasewebClient(self.api_token, self.override_domain)

    def test_add_record(self):
        """feature: create a DNS record.

        Given a domain name, a record name, and some content
        When I add a new DNS record
        Then a new DNS record should be created
        And it should be of type 'TXT' by default.
        """
        with requests_mock.Mocker() as mock:
            # Mock the response for `LeasewebClient#domains`.
            mock.get(
                (
                    f"{LEASEWEB_DOMAIN_API_ENDPOINT}"
                    f"?offset=0"
                    f"&limit={LEASEWEB_DOMAIN_API_LIST_LIMIT}"
                    f"&type=dns"
                ),
                status_code=200,
                json={
                    "domains": [{"domainName": self.override_record_domain}],
                    "_metadata": {"totalCount": 1},
                },
            )

            mock.post(
                str(
                    f"{LEASEWEB_DOMAIN_API_ENDPOINT}"
                    f"/{self.override_record_domain}/resourceRecordSets"
                ),
                status_code=201,
            )
            # Default type and ttl
            self.client.add_record(
                self.record_domain, self.record_name, self.record_content
            )
            # Explicit type and TTL
            self.client.add_record(
                self.record_domain,
                self.record_name,
                self.record_content,
                "TXT",
                self.record_ttl,
            )

    def test_delete_record(self):
        """feature: delete a DNS record

        Given a domain name and a record name
        When I delete a DNS record
        Then the DNS record should be removed
        And it should be of type 'TXT' by default.
        """
        with requests_mock.Mocker() as mock:
            # Mock the response for `LeasewebClient#domains`.
            mock.get(
                (
                    f"{LEASEWEB_DOMAIN_API_ENDPOINT}"
                    f"?offset=0"
                    f"&limit={LEASEWEB_DOMAIN_API_LIST_LIMIT}"
                    f"&type=dns"
                ),
                status_code=200,
                json={
                    "domains": [{"domainName": self.override_record_domain}],
                    "_metadata": {"totalCount": 1},
                },
            )

            mock.delete(
                (
                    f"{LEASEWEB_DOMAIN_API_ENDPOINT}/"
                    f"{self.override_record_domain}/resourceRecordSets/"
                    f"{self.override_record_name}./TXT"
                ),
                status_code=204,
            )

            # Default type
            self.client.delete_record(
                self.record_domain,
                self.record_name,
            )
            # Explicit type
            self.client.delete_record(
                self.record_domain,
                self.record_name,
                "TXT",
            )

    def test_get_managed_domain_name(self):
        """feature: Strip subdomains to find owned domain

        Given I have a domain of "example.com"
        When I request a certificate for "subdomain.example.com"
        Then the certbot plugin should add a record to "example.com"
        """

        with requests_mock.Mocker() as mock:
            # Mock the response for `LeasewebClient#domains`.
            mock.get(
                (
                    f"{LEASEWEB_DOMAIN_API_ENDPOINT}"
                    f"?offset=0"
                    f"&limit={LEASEWEB_DOMAIN_API_LIST_LIMIT}"
                    f"&type=dns"
                ),
                status_code=200,
                json={
                    "domains": [{"domainName": self.override_record_domain}],
                    "_metadata": {"totalCount": 1},
                },
            )

            for subdomain in ["test", "test.test", "test.test.test"]:
                # pylint: disable=protected-access
                managed_domain = self.client._get_managed_domain_name(
                    f"{subdomain}.{self.override_record_domain}"
                )

                assert managed_domain == self.override_record_domain

            try:
                # pylint: disable=protected-access
                self.client._get_managed_domain_name(secrets.token_hex(32))
            except Exception as _exc:  # pylint: disable=broad-exception-caught
                assert (
                    False
                ), "'_get_managed_domain_name' should not raise an exception with override_domain"


if __name__ == "__main__":
    unittest.main()

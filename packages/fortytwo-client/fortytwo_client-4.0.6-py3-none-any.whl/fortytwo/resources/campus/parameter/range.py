from datetime import datetime

from fortytwo.request.parameter.parameter import Range


class CampusRange:
    """
    Range class specifically for campus resources with all supported 42 API range fields.
    """

    @staticmethod
    def id_range(min_id: str | int | None = None, max_id: str | int | None = None) -> Range:
        """
        Filter campuses by ID range.

        Args:
            min_id (Union[str, int], optional): Minimum ID value.
            max_id (Union[str, int], optional): Maximum ID value.
        """
        return Range("id", [min_id, max_id])

    @staticmethod
    def name_range(min_name: str | None = None, max_name: str | None = None) -> Range:
        """
        Filter campuses by name range (alphabetical).

        Args:
            min_name (str, optional): Minimum name value.
            max_name (str, optional): Maximum name value.
        """
        return Range("name", [min_name, max_name])

    @staticmethod
    def created_at_range(
        start_date: str | datetime | None = None, end_date: str | datetime | None = None
    ) -> Range:
        """
        Filter campuses by created date range.

        Args:
            start_date (Union[str, datetime], optional): Start date (ISO format string or datetime object).
            end_date (Union[str, datetime], optional): End date (ISO format string or datetime object).
        """
        return Range("created_at", [start_date, end_date])

    @staticmethod
    def updated_at_range(
        start_date: str | datetime | None = None, end_date: str | datetime | None = None
    ) -> Range:
        """
        Filter campuses by updated date range.

        Args:
            start_date (Union[str, datetime], optional): Start date (ISO format string or datetime object).
            end_date (Union[str, datetime], optional): End date (ISO format string or datetime object).
        """
        return Range("updated_at", [start_date, end_date])

    @staticmethod
    def time_zone_range(min_tz: str | None = None, max_tz: str | None = None) -> Range:
        """
        Filter campuses by time zone range.

        Args:
            min_tz (str, optional): Minimum time zone value.
            max_tz (str, optional): Maximum time zone value.
        """
        return Range("time_zone", [min_tz, max_tz])

    @staticmethod
    def language_id_range(
        min_id: str | int | None = None, max_id: str | int | None = None
    ) -> Range:
        """
        Filter campuses by language ID range.

        Args:
            min_id (Union[str, int], optional): Minimum language ID value.
            max_id (Union[str, int], optional): Maximum language ID value.
        """
        return Range("language_id", [min_id, max_id])

    @staticmethod
    def slug_range(min_slug: str | None = None, max_slug: str | None = None) -> Range:
        """
        Filter campuses by slug range.

        Args:
            min_slug (str, optional): Minimum slug value.
            max_slug (str, optional): Maximum slug value.
        """
        return Range("slug", [min_slug, max_slug])

    @staticmethod
    def main_email_range(min_email: str | None = None, max_email: str | None = None) -> Range:
        """
        Filter campuses by main email range.

        Args:
            min_email (str, optional): Minimum email value.
            max_email (str, optional): Maximum email value.
        """
        return Range("main_email", [min_email, max_email])

    @staticmethod
    def endpoint_id_range(
        min_id: str | int | None = None, max_id: str | int | None = None
    ) -> Range:
        """
        Filter campuses by endpoint ID range.

        Args:
            min_id (Union[str, int], optional): Minimum endpoint ID value.
            max_id (Union[str, int], optional): Maximum endpoint ID value.
        """
        return Range("endpoint_id", [min_id, max_id])

    @staticmethod
    def vogsphere_id_range(
        min_id: str | int | None = None, max_id: str | int | None = None
    ) -> Range:
        """
        Filter campuses by vogsphere ID range.

        Args:
            min_id (Union[str, int], optional): Minimum vogsphere ID value.
            max_id (Union[str, int], optional): Maximum vogsphere ID value.
        """
        return Range("vogsphere_id", [min_id, max_id])

    @staticmethod
    def content_email_range(min_email: str | None = None, max_email: str | None = None) -> Range:
        """
        Filter campuses by content email range.

        Args:
            min_email (str, optional): Minimum email value.
            max_email (str, optional): Maximum email value.
        """
        return Range("content_email", [min_email, max_email])

    @staticmethod
    def time_of_community_service_started_range(
        start_time: str | datetime | None = None, end_time: str | datetime | None = None
    ) -> Range:
        """
        Filter campuses by time of community service started range.

        Args:
            start_time (Union[str, datetime], optional): Start time (ISO format string or datetime object).
            end_time (Union[str, datetime], optional): End time (ISO format string or datetime object).
        """
        return Range("time_of_community_service_started", [start_time, end_time])

    @staticmethod
    def companies_mail_range(min_email: str | None = None, max_email: str | None = None) -> Range:
        """
        Filter campuses by companies mail range.

        Args:
            min_email (str, optional): Minimum email value.
            max_email (str, optional): Maximum email value.
        """
        return Range("companies_mail", [min_email, max_email])

    @staticmethod
    def address_range(min_addr: str | None = None, max_addr: str | None = None) -> Range:
        """
        Filter campuses by address range.

        Args:
            min_addr (str, optional): Minimum address value.
            max_addr (str, optional): Maximum address value.
        """
        return Range("address", [min_addr, max_addr])

    @staticmethod
    def zip_range(min_zip: str | None = None, max_zip: str | None = None) -> Range:
        """
        Filter campuses by zip code range.

        Args:
            min_zip (str, optional): Minimum zip code value.
            max_zip (str, optional): Maximum zip code value.
        """
        return Range("zip", [min_zip, max_zip])

    @staticmethod
    def city_range(min_city: str | None = None, max_city: str | None = None) -> Range:
        """
        Filter campuses by city range.

        Args:
            min_city (str, optional): Minimum city value.
            max_city (str, optional): Maximum city value.
        """
        return Range("city", [min_city, max_city])

    @staticmethod
    def country_range(min_country: str | None = None, max_country: str | None = None) -> Range:
        """
        Filter campuses by country range.

        Args:
            min_country (str, optional): Minimum country value.
            max_country (str, optional): Maximum country value.
        """
        return Range("country", [min_country, max_country])

    @staticmethod
    def pro_needs_validation_range(
        min_val: bool | None = None, max_val: bool | None = None
    ) -> Range:
        """
        Filter campuses by pro needs validation range.

        Args:
            min_val (bool, optional): Minimum validation value.
            max_val (bool, optional): Maximum validation value.
        """
        return Range("pro_needs_validation", [min_val, max_val])

    @staticmethod
    def logo_range(min_logo: str | None = None, max_logo: str | None = None) -> Range:
        """
        Filter campuses by logo range.

        Args:
            min_logo (str, optional): Minimum logo value.
            max_logo (str, optional): Maximum logo value.
        """
        return Range("logo", [min_logo, max_logo])

    @staticmethod
    def website_range(min_url: str | None = None, max_url: str | None = None) -> Range:
        """
        Filter campuses by website range.

        Args:
            min_url (str, optional): Minimum URL value.
            max_url (str, optional): Maximum URL value.
        """
        return Range("website", [min_url, max_url])

    @staticmethod
    def facebook_range(min_url: str | None = None, max_url: str | None = None) -> Range:
        """
        Filter campuses by facebook range.

        Args:
            min_url (str, optional): Minimum URL value.
            max_url (str, optional): Maximum URL value.
        """
        return Range("facebook", [min_url, max_url])

    @staticmethod
    def twitter_range(min_url: str | None = None, max_url: str | None = None) -> Range:
        """
        Filter campuses by twitter range.

        Args:
            min_url (str, optional): Minimum URL value.
            max_url (str, optional): Maximum URL value.
        """
        return Range("twitter", [min_url, max_url])

    @staticmethod
    def display_name_range(min_name: str | None = None, max_name: str | None = None) -> Range:
        """
        Filter campuses by display name range.

        Args:
            min_name (str, optional): Minimum display name value.
            max_name (str, optional): Maximum display name value.
        """
        return Range("display_name", [min_name, max_name])

    @staticmethod
    def email_extension_range(min_ext: str | None = None, max_ext: str | None = None) -> Range:
        """
        Filter campuses by email extension range.

        Args:
            min_ext (str, optional): Minimum extension value.
            max_ext (str, optional): Maximum extension value.
        """
        return Range("email_extension", [min_ext, max_ext])

    @staticmethod
    def help_url_range(min_url: str | None = None, max_url: str | None = None) -> Range:
        """
        Filter campuses by help URL range.

        Args:
            min_url (str, optional): Minimum URL value.
            max_url (str, optional): Maximum URL value.
        """
        return Range("help_url", [min_url, max_url])

    @staticmethod
    def active_range(min_val: bool | None = None, max_val: bool | None = None) -> Range:
        """
        Filter campuses by active status range.

        Args:
            min_val (bool, optional): Minimum active value.
            max_val (bool, optional): Maximum active value.
        """
        return Range("active", [min_val, max_val])

    @staticmethod
    def open_to_job_offers_range(min_val: bool | None = None, max_val: bool | None = None) -> Range:
        """
        Filter campuses by open to job offers range.

        Args:
            min_val (bool, optional): Minimum value.
            max_val (bool, optional): Maximum value.
        """
        return Range("open_to_job_offers", [min_val, max_val])

    @staticmethod
    def default_hidden_phone_range(
        min_val: bool | None = None, max_val: bool | None = None
    ) -> Range:
        """
        Filter campuses by default hidden phone range.

        Args:
            min_val (bool, optional): Minimum value.
            max_val (bool, optional): Maximum value.
        """
        return Range("default_hidden_phone", [min_val, max_val])

    @staticmethod
    def tig_email_range(min_email: str | None = None, max_email: str | None = None) -> Range:
        """
        Filter campuses by TIG email range.

        Args:
            min_email (str, optional): Minimum email value.
            max_email (str, optional): Maximum email value.
        """
        return Range("tig_email", [min_email, max_email])

    @staticmethod
    def minimum_slot_duration_range(
        min_duration: int | None = None, max_duration: int | None = None
    ) -> Range:
        """
        Filter campuses by minimum slot duration range.

        Args:
            min_duration (int, optional): Minimum duration value.
            max_duration (int, optional): Maximum duration value.
        """
        return Range("minimum_slot_duration", [min_duration, max_duration])

    @staticmethod
    def alumni_system_range(min_val: bool | None = None, max_val: bool | None = None) -> Range:
        """
        Filter campuses by alumni system range.

        Args:
            min_val (bool, optional): Minimum value.
            max_val (bool, optional): Maximum value.
        """
        return Range("alumni_system", [min_val, max_val])

    @staticmethod
    def manual_alumnization_before_first_internship_range(
        min_val: bool | None = None, max_val: bool | None = None
    ) -> Range:
        """
        Filter campuses by manual alumnization before first internship range.

        Args:
            min_val (bool, optional): Minimum value.
            max_val (bool, optional): Maximum value.
        """
        return Range("manual_alumnization_before_first_internship", [min_val, max_val])

    @staticmethod
    def public_range(min_val: bool | None = None, max_val: bool | None = None) -> Range:
        """
        Filter campuses by public status range.

        Args:
            min_val (bool, optional): Minimum value.
            max_val (bool, optional): Maximum value.
        """
        return Range("public", [min_val, max_val])

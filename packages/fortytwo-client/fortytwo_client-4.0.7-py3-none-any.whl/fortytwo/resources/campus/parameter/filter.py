from datetime import datetime

from fortytwo.request.parameter.parameter import Filter


class CampusFilter:
    """
    Filter class specifically for campus resources with all supported 42 API filters.
    """

    @staticmethod
    def by_id(campus_id: str | int) -> Filter:
        """
        Filter campuses by ID.

        Args:
            campus_id (Union[str, int]): The campus ID to filter by.
        """
        return Filter("id", [campus_id])

    @staticmethod
    def by_name(name: str) -> Filter:
        """
        Filter campuses by name.

        Args:
            name (str): The campus name to filter by.
        """
        return Filter("name", [name])

    @staticmethod
    def by_created_at(created_at: str | datetime) -> Filter:
        """
        Filter campuses by created date.

        Args:
            created_at (Union[str, datetime]): The creation date to filter by (ISO format string or datetime object).
        """
        return Filter("created_at", [created_at])

    @staticmethod
    def by_updated_at(updated_at: str | datetime) -> Filter:
        """
        Filter campuses by updated date.

        Args:
            updated_at (Union[str, datetime]): The update date to filter by (ISO format string or datetime object).
        """
        return Filter("updated_at", [updated_at])

    @staticmethod
    def by_time_zone(time_zone: str) -> Filter:
        """
        Filter campuses by time zone.

        Args:
            time_zone (str): The time zone to filter by.
        """
        return Filter("time_zone", [time_zone])

    @staticmethod
    def by_language_id(language_id: str | int) -> Filter:
        """
        Filter campuses by language ID.

        Args:
            language_id (Union[str, int]): The language ID to filter by.
        """
        return Filter("language_id", [language_id])

    @staticmethod
    def by_slug(slug: str) -> Filter:
        """
        Filter campuses by slug.

        Args:
            slug (str): The slug to filter by.
        """
        return Filter("slug", [slug])

    @staticmethod
    def by_main_email(main_email: str) -> Filter:
        """
        Filter campuses by main email.

        Args:
            main_email (str): The main email to filter by.
        """
        return Filter("main_email", [main_email])

    @staticmethod
    def by_endpoint_id(endpoint_id: str | int) -> Filter:
        """
        Filter campuses by endpoint ID.

        Args:
            endpoint_id (Union[str, int]): The endpoint ID to filter by.
        """
        return Filter("endpoint_id", [endpoint_id])

    @staticmethod
    def by_vogsphere_id(vogsphere_id: str | int) -> Filter:
        """
        Filter campuses by vogsphere ID.

        Args:
            vogsphere_id (Union[str, int]): The vogsphere ID to filter by.
        """
        return Filter("vogsphere_id", [vogsphere_id])

    @staticmethod
    def by_content_email(content_email: str) -> Filter:
        """
        Filter campuses by content email.

        Args:
            content_email (str): The content email to filter by.
        """
        return Filter("content_email", [content_email])

    @staticmethod
    def by_time_of_community_service_started(time: str | datetime) -> Filter:
        """
        Filter campuses by time of community service started.

        Args:
            time (Union[str, datetime]): The time to filter by (ISO format string or datetime object).
        """
        return Filter("time_of_community_service_started", [time])

    @staticmethod
    def by_companies_mail(companies_mail: str) -> Filter:
        """
        Filter campuses by companies mail.

        Args:
            companies_mail (str): The companies mail to filter by.
        """
        return Filter("companies_mail", [companies_mail])

    @staticmethod
    def by_address(address: str) -> Filter:
        """
        Filter campuses by address.

        Args:
            address (str): The address to filter by.
        """
        return Filter("address", [address])

    @staticmethod
    def by_zip(zip_code: str) -> Filter:
        """
        Filter campuses by zip code.

        Args:
            zip_code (str): The zip code to filter by.
        """
        return Filter("zip", [zip_code])

    @staticmethod
    def by_city(city: str) -> Filter:
        """
        Filter campuses by city.

        Args:
            city (str): The city to filter by.
        """
        return Filter("city", [city])

    @staticmethod
    def by_country(country: str) -> Filter:
        """
        Filter campuses by country.

        Args:
            country (str): The country to filter by.
        """
        return Filter("country", [country])

    @staticmethod
    def by_pro_needs_validation(pro_needs_validation: bool) -> Filter:
        """
        Filter campuses by pro needs validation.

        Args:
            pro_needs_validation (bool): The pro needs validation status to filter by.
        """
        return Filter("pro_needs_validation", [pro_needs_validation])

    @staticmethod
    def by_logo(logo: str) -> Filter:
        """
        Filter campuses by logo.

        Args:
            logo (str): The logo to filter by.
        """
        return Filter("logo", [logo])

    @staticmethod
    def by_website(website: str) -> Filter:
        """
        Filter campuses by website.

        Args:
            website (str): The website to filter by.
        """
        return Filter("website", [website])

    @staticmethod
    def by_facebook(facebook: str) -> Filter:
        """
        Filter campuses by facebook.

        Args:
            facebook (str): The facebook URL to filter by.
        """
        return Filter("facebook", [facebook])

    @staticmethod
    def by_twitter(twitter: str) -> Filter:
        """
        Filter campuses by twitter.

        Args:
            twitter (str): The twitter URL to filter by.
        """
        return Filter("twitter", [twitter])

    @staticmethod
    def by_display_name(display_name: str) -> Filter:
        """
        Filter campuses by display name.

        Args:
            display_name (str): The display name to filter by.
        """
        return Filter("display_name", [display_name])

    @staticmethod
    def by_email_extension(email_extension: str) -> Filter:
        """
        Filter campuses by email extension.

        Args:
            email_extension (str): The email extension to filter by.
        """
        return Filter("email_extension", [email_extension])

    @staticmethod
    def by_help_url(help_url: str) -> Filter:
        """
        Filter campuses by help URL.

        Args:
            help_url (str): The help URL to filter by.
        """
        return Filter("help_url", [help_url])

    @staticmethod
    def by_active(active: bool) -> Filter:
        """
        Filter campuses by active status.

        Args:
            active (bool): The active status to filter by.
        """
        return Filter("active", [active])

    @staticmethod
    def by_open_to_job_offers(open_to_job_offers: bool) -> Filter:
        """
        Filter campuses by open to job offers.

        Args:
            open_to_job_offers (bool): The open to job offers status to filter by.
        """
        return Filter("open_to_job_offers", [open_to_job_offers])

    @staticmethod
    def by_default_hidden_phone(default_hidden_phone: bool) -> Filter:
        """
        Filter campuses by default hidden phone.

        Args:
            default_hidden_phone (bool): The default hidden phone status to filter by.
        """
        return Filter("default_hidden_phone", [default_hidden_phone])

    @staticmethod
    def by_tig_email(tig_email: str) -> Filter:
        """
        Filter campuses by TIG email.

        Args:
            tig_email (str): The TIG email to filter by.
        """
        return Filter("tig_email", [tig_email])

    @staticmethod
    def by_minimum_slot_duration(minimum_slot_duration: int) -> Filter:
        """
        Filter campuses by minimum slot duration.

        Args:
            minimum_slot_duration (int): The minimum slot duration to filter by.
        """
        return Filter("minimum_slot_duration", [minimum_slot_duration])

    @staticmethod
    def by_alumni_system(alumni_system: bool) -> Filter:
        """
        Filter campuses by alumni system.

        Args:
            alumni_system (bool): The alumni system status to filter by.
        """
        return Filter("alumni_system", [alumni_system])

    @staticmethod
    def by_manual_alumnization_before_first_internship(value: bool) -> Filter:
        """
        Filter campuses by manual alumnization before first internship.

        Args:
            value (bool): The manual alumnization before first internship status to filter by.
        """
        return Filter("manual_alumnization_before_first_internship", [value])

    @staticmethod
    def by_public(public: bool) -> Filter:
        """
        Filter campuses by public status.

        Args:
            public (bool): The public status to filter by.
        """
        return Filter("public", [public])

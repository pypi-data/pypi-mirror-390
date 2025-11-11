from fortytwo.request.parameter.parameter import Sort, SortDirection


class CampusSort:
    """
    Sort class specifically for campus resources with all supported 42 API sort fields.
    """

    @staticmethod
    def by_id(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort by ID (default descending).

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("id", direction)])

    @staticmethod
    def by_name(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort by name.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("name", direction)])

    @staticmethod
    def by_created_at(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort by created date.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("created_at", direction)])

    @staticmethod
    def by_updated_at(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort by updated date.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("updated_at", direction)])

    @staticmethod
    def by_time_zone(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort by time zone.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("time_zone", direction)])

    @staticmethod
    def by_language_id(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort by language ID.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("language_id", direction)])

    @staticmethod
    def by_slug(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort by slug.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("slug", direction)])

    @staticmethod
    def by_main_email(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort by main email.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("main_email", direction)])

    @staticmethod
    def by_endpoint_id(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort by endpoint ID.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("endpoint_id", direction)])

    @staticmethod
    def by_vogsphere_id(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort by vogsphere ID.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("vogsphere_id", direction)])

    @staticmethod
    def by_content_email(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort by content email.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("content_email", direction)])

    @staticmethod
    def by_time_of_community_service_started(
        direction: SortDirection = SortDirection.DESCENDING,
    ) -> Sort:
        """
        Sort by time of community service started.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("time_of_community_service_started", direction)])

    @staticmethod
    def by_companies_mail(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort by companies mail.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("companies_mail", direction)])

    @staticmethod
    def by_address(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort by address.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("address", direction)])

    @staticmethod
    def by_zip(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort by zip code.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("zip", direction)])

    @staticmethod
    def by_city(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort by city.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("city", direction)])

    @staticmethod
    def by_country(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort by country.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("country", direction)])

    @staticmethod
    def by_pro_needs_validation(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort by pro needs validation.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("pro_needs_validation", direction)])

    @staticmethod
    def by_logo(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort by logo.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("logo", direction)])

    @staticmethod
    def by_website(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort by website.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("website", direction)])

    @staticmethod
    def by_facebook(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort by facebook.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("facebook", direction)])

    @staticmethod
    def by_twitter(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort by twitter.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("twitter", direction)])

    @staticmethod
    def by_display_name(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort by display name.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("display_name", direction)])

    @staticmethod
    def by_email_extension(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort by email extension.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("email_extension", direction)])

    @staticmethod
    def by_help_url(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort by help URL.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("help_url", direction)])

    @staticmethod
    def by_active(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort by active status.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("active", direction)])

    @staticmethod
    def by_open_to_job_offers(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort by open to job offers.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("open_to_job_offers", direction)])

    @staticmethod
    def by_default_hidden_phone(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort by default hidden phone.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("default_hidden_phone", direction)])

    @staticmethod
    def by_tig_email(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort by TIG email.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("tig_email", direction)])

    @staticmethod
    def by_minimum_slot_duration(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort by minimum slot duration.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("minimum_slot_duration", direction)])

    @staticmethod
    def by_alumni_system(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort by alumni system.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("alumni_system", direction)])

    @staticmethod
    def by_manual_alumnization_before_first_internship(
        direction: SortDirection = SortDirection.DESCENDING,
    ) -> Sort:
        """
        Sort by manual alumnization before first internship.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("manual_alumnization_before_first_internship", direction)])

    @staticmethod
    def by_public(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort by public status.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("public", direction)])

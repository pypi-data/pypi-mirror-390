from itemadapter import ItemAdapter

from crawler_utils.talisman_job_env import TalismanJobEnvironment


class TalismanMessageMetadataPipeline:
    def __init__(self, job_env):
        message_metadata = {
            "_job_id": job_env.job_id,
            "_periodic_job_id": job_env.periodic_job_id,
            "_project_id": job_env.project_id,
            "_crawler_id": job_env.crawler_id,
            "_external_search_loader_id": job_env.external_search_loader_id,
            "_research_map_id": job_env.research_map_id
        }
        self.message_metadata = {key: value for key, value in message_metadata.items() if value}

    @classmethod
    def from_crawler(cls, crawler):
        return cls(TalismanJobEnvironment.from_settings(crawler.settings))

    def process_item(self, item, spider):
        item_dict = ItemAdapter(item).asdict()
        item_dict.update(self.message_metadata)
        return item_dict

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from pydantic import Tag

from modelhub.clients.prompts import PromptClient
from modelhub.core import ModelHubAPIException
from modelhub.models.models import (
    Alias,
    SearchModelsCriteria,
    UpdatePromptVersionTagsRequest,
)
from modelhub.models.prompts import (
    EvaluationInput,
    PromptCreation,
    PromptRunTracesDto,
    UpdatePromptVersionRequest,
)


class TestPromptClient:
    """Test suite for PromptClient"""

    @pytest.fixture
    def mock_credential(self):
        """Mock credential fixture"""
        credential = MagicMock()
        credential.get_token = MagicMock(return_value="mock-token")
        credential.aget_token = AsyncMock(return_value="mock-token")
        return credential

    @pytest.fixture
    def prompt_client(self, mock_credential):
        """PromptClient fixture"""
        return PromptClient(
            credential=mock_credential,
            client_id="test-client",
        )

    @pytest.fixture
    def sample_prompt_creation(self):
        """Sample PromptCreation fixture"""
        return MagicMock(spec=PromptCreation)

    @pytest.fixture
    def sample_search_criteria(self):
        """Sample SearchModelsCriteria fixture"""
        return MagicMock(spec=SearchModelsCriteria)

    @pytest.fixture
    def sample_update_request(self):
        """Sample UpdatePromptVersionRequest fixture"""
        return MagicMock(spec=UpdatePromptVersionRequest)

    @pytest.fixture
    def sample_tag(self):
        """Sample Tag fixture"""
        return MagicMock(spec=Tag)

    @pytest.fixture
    def sample_alias(self):
        """Sample Alias fixture"""
        return MagicMock(spec=Alias)

    @pytest.fixture
    def sample_evaluation_input(self):
        """Sample EvaluationInput fixture"""
        return MagicMock(spec=EvaluationInput)

    @pytest.fixture
    def sample_traces_dto(self):
        """Sample PromptRunTracesDto fixture"""
        return MagicMock(spec=PromptRunTracesDto)

    # Test create_prompt
    def test_create_prompt_success(self, prompt_client, sample_prompt_creation):
        """Test successful prompt creation"""
        expected_response = {"id": "prompt-123", "name": "test-prompt"}

        with patch.object(
            prompt_client, "post", return_value=expected_response
        ) as mock_post:
            result = prompt_client.create_prompt(sample_prompt_creation)

            assert result == expected_response
            mock_post.assert_called_once_with("prompts/", json=sample_prompt_creation)

    def test_create_prompt_error(self, prompt_client, sample_prompt_creation):
        """Test prompt creation with error"""
        with patch.object(
            prompt_client, "post", side_effect=httpx.RequestError("Connection failed")
        ):
            with pytest.raises(ModelHubAPIException) as exc_info:
                prompt_client.create_prompt(sample_prompt_creation)

            assert "error creating prompt" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_acreate_prompt_success(self, prompt_client, sample_prompt_creation):
        """Test successful async prompt creation"""
        expected_response = {"id": "prompt-123", "name": "test-prompt"}

        with patch.object(
            prompt_client, "apost", return_value=expected_response
        ) as mock_apost:
            result = await prompt_client.acreate_prompt(sample_prompt_creation)

            assert result == expected_response
            mock_apost.assert_called_once_with("prompts/", json=sample_prompt_creation)

    @pytest.mark.asyncio
    async def test_acreate_prompt_error(self, prompt_client, sample_prompt_creation):
        """Test async prompt creation with error"""
        with patch.object(
            prompt_client, "apost", side_effect=httpx.RequestError("Connection failed")
        ):
            with pytest.raises(ModelHubAPIException) as exc_info:
                await prompt_client.acreate_prompt(sample_prompt_creation)

            assert "error creating prompt" in str(exc_info.value)

    # Test get_prompts
    def test_get_prompts_success(self, prompt_client, sample_search_criteria):
        """Test successful get prompts"""
        expected_response = [{"id": "prompt-1"}, {"id": "prompt-2"}]

        with patch.object(
            prompt_client, "post", return_value=expected_response
        ) as mock_post:
            result = prompt_client.get_prompts(sample_search_criteria)

            assert result == expected_response
            mock_post.assert_called_once_with(
                "prompts/search", json=sample_search_criteria
            )

    def test_get_prompts_error(self, prompt_client, sample_search_criteria):
        """Test get prompts with error"""
        with patch.object(
            prompt_client, "post", side_effect=httpx.RequestError("Connection failed")
        ):
            with pytest.raises(ModelHubAPIException) as exc_info:
                prompt_client.get_prompts(sample_search_criteria)

            assert "error getting prompt" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_aget_prompts_success(self, prompt_client, sample_search_criteria):
        """Test successful async get prompts"""
        expected_response = [{"id": "prompt-1"}, {"id": "prompt-2"}]

        with patch.object(
            prompt_client, "apost", return_value=expected_response
        ) as mock_apost:
            result = await prompt_client.aget_prompts(sample_search_criteria)

            assert result == expected_response
            mock_apost.assert_called_once_with(
                "prompts/search", json=sample_search_criteria
            )

    # Test get_prompt_versions
    def test_get_prompt_versions_success(self, prompt_client):
        """Test successful get prompt versions"""
        expected_response = [{"version": 1}, {"version": 2}]

        with patch.object(
            prompt_client, "get", return_value=expected_response
        ) as mock_get:
            result = prompt_client.get_prompt_versions()

            assert result == expected_response
            mock_get.assert_called_once_with("prompts/versions/search")

    def test_get_prompt_versions_error(self, prompt_client):
        """Test get prompt versions with error"""
        with patch.object(
            prompt_client, "get", side_effect=httpx.RequestError("Connection failed")
        ):
            with pytest.raises(ModelHubAPIException) as exc_info:
                prompt_client.get_prompt_versions()

            assert "error getting prompt versions" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_aget_prompt_versions_success(self, prompt_client):
        """Test successful async get prompt versions"""
        expected_response = [{"version": 1}, {"version": 2}]

        with patch.object(
            prompt_client, "aget", return_value=expected_response
        ) as mock_aget:
            result = await prompt_client.aget_prompt_versions()

            assert result == expected_response
            mock_aget.assert_called_once_with("prompts/versions/search")

    # Test get_prompt_versions_with_name
    def test_get_prompt_versions_with_name_success(self, prompt_client):
        """Test successful get prompt versions with name"""
        expected_response = [{"version": 1}, {"version": 2}]
        prompt_name = "test-prompt"

        with patch.object(
            prompt_client, "get", return_value=expected_response
        ) as mock_get:
            result = prompt_client.get_prompt_versions_with_name(prompt_name)

            assert result == expected_response
            mock_get.assert_called_once_with(f"prompts/{prompt_name}/versions/search")

    @pytest.mark.asyncio
    async def test_aget_prompt_versions_with_name_success(self, prompt_client):
        """Test successful async get prompt versions with name"""
        expected_response = [{"version": 1}, {"version": 2}]
        prompt_name = "test-prompt"

        with patch.object(
            prompt_client, "aget", return_value=expected_response
        ) as mock_aget:
            result = await prompt_client.aget_prompt_versions_with_name(prompt_name)

            assert result == expected_response
            mock_aget.assert_called_once_with(f"prompts/{prompt_name}/versions/search")

    # Test get_registered_prompt_by_name
    def test_get_registered_prompt_by_name_success(self, prompt_client):
        """Test successful get registered prompt by name"""
        expected_response = {"id": "prompt-123", "name": "test-prompt"}
        prompt_name = "test-prompt"

        with patch.object(
            prompt_client, "get", return_value=expected_response
        ) as mock_get:
            result = prompt_client.get_registered_prompt_by_name(prompt_name)

            assert result == expected_response
            mock_get.assert_called_once_with(f"prompts/{prompt_name}")

    @pytest.mark.asyncio
    async def test_aget_registered_prompt_by_name_success(self, prompt_client):
        """Test successful async get registered prompt by name"""
        expected_response = {"id": "prompt-123", "name": "test-prompt"}
        prompt_name = "test-prompt"

        with patch.object(
            prompt_client, "aget", return_value=expected_response
        ) as mock_aget:
            result = await prompt_client.aget_registered_prompt_by_name(prompt_name)

            assert result == expected_response
            mock_aget.assert_called_once_with(f"prompts/{prompt_name}")

    # Test delete_prompt
    def test_delete_prompt_success(self, prompt_client):
        """Test successful prompt deletion"""
        expected_response = {"message": "Prompt deleted successfully"}
        prompt_name = "test-prompt"

        with patch.object(
            prompt_client, "delete", return_value=expected_response
        ) as mock_delete:
            result = prompt_client.delete_prompt(prompt_name)

            assert result == expected_response
            mock_delete.assert_called_once_with(f"prompts/{prompt_name}")

    def test_delete_prompt_error(self, prompt_client):
        """Test prompt deletion with error"""
        prompt_name = "test-prompt"

        with patch.object(
            prompt_client, "delete", side_effect=httpx.RequestError("Connection failed")
        ):
            with pytest.raises(ModelHubAPIException) as exc_info:
                prompt_client.delete_prompt(prompt_name)

            assert "error deleting prompt" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_adelete_prompt_success(self, prompt_client):
        """Test successful async prompt deletion"""
        expected_response = {"message": "Prompt deleted successfully"}
        prompt_name = "test-prompt"

        with patch.object(
            prompt_client, "adelete", return_value=expected_response
        ) as mock_adelete:
            result = await prompt_client.adelete_prompt(prompt_name)

            assert result == expected_response
            mock_adelete.assert_called_once_with(f"prompts/{prompt_name}")

    # Test create_prompt_version
    def test_create_prompt_version_success(self, prompt_client, sample_update_request):
        """Test successful prompt version creation"""
        expected_response = {"version": 2, "id": "version-456"}
        prompt_name = "test-prompt"

        with patch.object(
            prompt_client, "post", return_value=expected_response
        ) as mock_post:
            result = prompt_client.create_prompt_version(
                prompt_name, sample_update_request
            )

            assert result == expected_response
            mock_post.assert_called_once_with(
                f"prompts/{prompt_name}/versions", json=sample_update_request
            )

    @pytest.mark.asyncio
    async def test_acreate_prompt_version_success(
        self, prompt_client, sample_update_request
    ):
        """Test successful async prompt version creation"""
        expected_response = {"version": 2, "id": "version-456"}
        prompt_name = "test-prompt"

        with patch.object(
            prompt_client, "apost", return_value=expected_response
        ) as mock_apost:
            result = await prompt_client.acreate_prompt_version(
                prompt_name, sample_update_request
            )

            assert result == expected_response
            mock_apost.assert_called_once_with(
                f"prompts/{prompt_name}/versions", json=sample_update_request
            )

    # Test create_tag
    def test_create_tag_success(self, prompt_client, sample_tag):
        """Test successful tag creation"""
        expected_response = {"message": "Tag created successfully"}
        prompt_name = "test-prompt"

        with patch.object(
            prompt_client, "post", return_value=expected_response
        ) as mock_post:
            result = prompt_client.create_tag(prompt_name, sample_tag)

            assert result == expected_response
            mock_post.assert_called_once_with(
                f"prompts/{prompt_name}/tags", json=sample_tag
            )

    @pytest.mark.asyncio
    async def test_acreate_tag_success(self, prompt_client, sample_tag):
        """Test successful async tag creation"""
        expected_response = {"message": "Tag created successfully"}
        prompt_name = "test-prompt"

        with patch.object(
            prompt_client, "apost", return_value=expected_response
        ) as mock_apost:
            result = await prompt_client.acreate_tag(prompt_name, sample_tag)

            assert result == expected_response
            mock_apost.assert_called_once_with(
                f"prompts/{prompt_name}/tags", json=sample_tag
            )

    # Test get_registered_prompt_version
    def test_get_registered_prompt_version_success(self, prompt_client):
        """Test successful get registered prompt version"""
        expected_response = {"version": 1, "template": "test template"}
        prompt_name = "test-prompt"
        version = 1

        with patch.object(
            prompt_client, "get", return_value=expected_response
        ) as mock_get:
            result = prompt_client.get_registered_prompt_version(prompt_name, version)

            assert result == expected_response
            mock_get.assert_called_once_with(
                f"prompts/{prompt_name}/versions/{version}"
            )

    @pytest.mark.asyncio
    async def test_aget_registered_prompt_version_success(self, prompt_client):
        """Test successful async get registered prompt version"""
        expected_response = {"version": 1, "template": "test template"}
        prompt_name = "test-prompt"
        version = 1

        with patch.object(
            prompt_client, "aget", return_value=expected_response
        ) as mock_aget:
            result = await prompt_client.aget_registered_prompt_version(
                prompt_name, version
            )

            assert result == expected_response
            mock_aget.assert_called_once_with(
                f"prompts/{prompt_name}/versions/{version}"
            )

    # Test update_prompt_version_tag
    def test_update_prompt_version_tag_success(self, prompt_client):
        """Test successful prompt version tag update"""
        expected_response = {"message": "Tags updated successfully"}
        prompt_name = "test-prompt"
        version = "1"
        tags = [MagicMock(spec=Tag)]

        with patch.object(
            prompt_client, "put", return_value=expected_response
        ) as mock_put:
            result = prompt_client.update_prompt_version_tag(prompt_name, version, tags)

            assert result == expected_response
            mock_put.assert_called_once_with(
                f"prompts/{prompt_name}/versions/{version}/tags", json=tags
            )

    @pytest.mark.asyncio
    async def test_aupdate_prompt_version_tag_success(self, prompt_client):
        """Test successful async prompt version tag update"""
        expected_response = {"message": "Tags updated successfully"}
        prompt_name = "test-prompt"
        version = "1"
        tags = [MagicMock(spec=Tag)]

        with patch.object(
            prompt_client, "aput", return_value=expected_response
        ) as mock_aput:
            result = await prompt_client.aupdate_prompt_version_tag(
                prompt_name, version, tags
            )

            assert result == expected_response
            mock_aput.assert_called_once_with(
                f"prompts/{prompt_name}/versions/{version}/tags", json=tags
            )

    # Test delete_prompt_version_tag
    def test_delete_prompt_version_tag_success(self, prompt_client):
        """Test successful prompt version tag deletion"""
        expected_response = {"message": "Tag deleted successfully"}
        prompt_name = "test-prompt"
        version = "1"
        tag_key = "environment"

        with patch.object(
            prompt_client, "delete", return_value=expected_response
        ) as mock_delete:
            result = prompt_client.delete_prompt_version_tag(
                prompt_name, version, tag_key
            )

            assert result == expected_response
            mock_delete.assert_called_once_with(
                f"prompts/{prompt_name}/versions/{version}/tags/{tag_key}"
            )

    @pytest.mark.asyncio
    async def test_adelete_prompt_version_tag_success(self, prompt_client):
        """Test successful async prompt version tag deletion"""
        expected_response = {"message": "Tag deleted successfully"}
        prompt_name = "test-prompt"
        version = "1"
        tag_key = "environment"

        with patch.object(
            prompt_client, "adelete", return_value=expected_response
        ) as mock_adelete:
            result = await prompt_client.adelete_prompt_version_tag(
                prompt_name, version, tag_key
            )

            assert result == expected_response
            mock_adelete.assert_called_once_with(
                f"prompts/{prompt_name}/versions/{version}/tags/{tag_key}"
            )

    # Test delete_tag
    def test_delete_tag_success(self, prompt_client):
        """Test successful tag deletion"""
        expected_response = {"message": "Tag deleted successfully"}
        prompt_name = "test-prompt"
        tag_key = "environment"

        with patch.object(
            prompt_client, "delete", return_value=expected_response
        ) as mock_delete:
            result = prompt_client.delete_tag(prompt_name, tag_key)

            assert result == expected_response
            mock_delete.assert_called_once_with(f"prompts/{prompt_name}/tags/{tag_key}")

    @pytest.mark.asyncio
    async def test_adelete_tag_success(self, prompt_client):
        """Test successful async tag deletion"""
        expected_response = {"message": "Tag deleted successfully"}
        prompt_name = "test-prompt"
        tag_key = "environment"

        with patch.object(
            prompt_client, "adelete", return_value=expected_response
        ) as mock_adelete:
            result = await prompt_client.adelete_tag(prompt_name, tag_key)

            assert result == expected_response
            mock_adelete.assert_called_once_with(
                f"prompts/{prompt_name}/tags/{tag_key}"
            )

    # Test create_alias
    def test_create_alias_success(self, prompt_client, sample_alias):
        """Test successful alias creation"""
        expected_response = {"message": "Alias created successfully"}
        prompt_name = "test-prompt"

        with patch.object(
            prompt_client, "post", return_value=expected_response
        ) as mock_post:
            result = prompt_client.create_alias(prompt_name, sample_alias)

            assert result == expected_response
            mock_post.assert_called_once_with(
                f"prompts/{prompt_name}/aliases", json=sample_alias
            )

    @pytest.mark.asyncio
    async def test_acreate_alias_success(self, prompt_client, sample_alias):
        """Test successful async alias creation"""
        expected_response = {"message": "Alias created successfully"}
        prompt_name = "test-prompt"

        with patch.object(
            prompt_client, "apost", return_value=expected_response
        ) as mock_apost:
            result = await prompt_client.acreate_alias(prompt_name, sample_alias)

            assert result == expected_response
            mock_apost.assert_called_once_with(
                f"prompts/{prompt_name}/aliases", json=sample_alias
            )

    # Test delete_alias
    def test_delete_alias_success(self, prompt_client):
        """Test successful alias deletion"""
        expected_response = {"message": "Alias deleted successfully"}
        prompt_name = "test-prompt"
        alias_name = "prod"

        with patch.object(
            prompt_client, "delete", return_value=expected_response
        ) as mock_delete:
            result = prompt_client.delete_alias(prompt_name, alias_name)

            assert result == expected_response
            mock_delete.assert_called_once_with(
                f"prompts/{prompt_name}/aliases/{alias_name}"
            )

    @pytest.mark.asyncio
    async def test_adelete_alias_success(self, prompt_client):
        """Test successful async alias deletion"""
        expected_response = {"message": "Alias deleted successfully"}
        prompt_name = "test-prompt"
        alias_name = "prod"

        with patch.object(
            prompt_client, "adelete", return_value=expected_response
        ) as mock_adelete:
            result = await prompt_client.adelete_alias(prompt_name, alias_name)

            assert result == expected_response
            mock_adelete.assert_called_once_with(
                f"prompts/{prompt_name}/aliases/{alias_name}"
            )

    # Test delete_prompt_version
    def test_delete_prompt_version_success(self, prompt_client):
        """Test successful prompt version deletion"""
        expected_response = {"message": "Version deleted successfully"}
        prompt_name = "test-prompt"
        version = 1

        with patch.object(
            prompt_client, "delete", return_value=expected_response
        ) as mock_delete:
            result = prompt_client.delete_prompt_version(prompt_name, version)

            assert result == expected_response
            mock_delete.assert_called_once_with(
                f"prompts/{prompt_name}/versions/{version}"
            )

    @pytest.mark.asyncio
    async def test_adelete_prompt_version_success(self, prompt_client):
        """Test successful async prompt version deletion"""
        expected_response = {"message": "Version deleted successfully"}
        prompt_name = "test-prompt"
        version = 1

        with patch.object(
            prompt_client, "adelete", return_value=expected_response
        ) as mock_adelete:
            result = await prompt_client.adelete_prompt_version(prompt_name, version)

            assert result == expected_response
            mock_adelete.assert_called_once_with(
                f"prompts/{prompt_name}/versions/{version}"
            )

    # Test update_prompt_version_tags
    def test_update_prompt_version_tags_success(self, prompt_client):
        """Test successful prompt version tags update"""
        expected_response = {"message": "Tags updated successfully"}
        prompt_name = "test-prompt"
        version = "1"
        tags_request = MagicMock(spec=UpdatePromptVersionTagsRequest)

        with patch.object(
            prompt_client, "put", return_value=expected_response
        ) as mock_put:
            result = prompt_client.update_prompt_version_tags(
                prompt_name, version, tags_request
            )

            assert result == expected_response
            mock_put.assert_called_once_with(
                f"prompts/{prompt_name}/versions/{version}/tags", json=tags_request
            )

    @pytest.mark.asyncio
    async def test_aupdate_prompt_version_tags_success(self, prompt_client):
        """Test successful async prompt version tags update"""
        expected_response = {"message": "Tags updated successfully"}
        prompt_name = "test-prompt"
        version = "1"
        tags_request = MagicMock(spec=UpdatePromptVersionTagsRequest)

        with patch.object(
            prompt_client, "aput", return_value=expected_response
        ) as mock_aput:
            result = await prompt_client.aupdate_prompt_version_tags(
                prompt_name, version, tags_request
            )

            assert result == expected_response
            mock_aput.assert_called_once_with(
                f"prompts/{prompt_name}/versions/{version}/tags", json=tags_request
            )

    # Test evaluate_prompt
    def test_evaluate_prompt_success(self, prompt_client, sample_evaluation_input):
        """Test successful prompt evaluation"""
        expected_response = {
            "metrics": {"accuracy": 0.95},
            "sample_prediction": "test result",
        }

        with patch.object(
            prompt_client, "post", return_value=expected_response
        ) as mock_post:
            result = prompt_client.evaluate_prompt(sample_evaluation_input)

            assert result == expected_response
            mock_post.assert_called_once_with(
                "prompts/evaluate-prompt", json=sample_evaluation_input
            )

    def test_evaluate_prompt_error(self, prompt_client, sample_evaluation_input):
        """Test prompt evaluation with error"""
        with patch.object(
            prompt_client, "post", side_effect=httpx.RequestError("Connection failed")
        ):
            with pytest.raises(ModelHubAPIException) as exc_info:
                prompt_client.evaluate_prompt(sample_evaluation_input)

            assert "error evaluating prompt" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_aevaluate_prompt_success(
        self, prompt_client, sample_evaluation_input
    ):
        """Test successful async prompt evaluation"""
        expected_response = {
            "metrics": {"accuracy": 0.95},
            "sample_prediction": "test result",
        }

        with patch.object(
            prompt_client, "apost", return_value=expected_response
        ) as mock_apost:
            result = await prompt_client.aevaluate_prompt(sample_evaluation_input)

            assert result == expected_response
            mock_apost.assert_called_once_with(
                "prompts/evaluate-prompt", json=sample_evaluation_input
            )

    # Test get_traces
    def test_get_traces_success(self, prompt_client, sample_traces_dto):
        """Test successful get traces"""
        expected_response = {"traces": [{"id": "trace-1"}, {"id": "trace-2"}]}

        with patch.object(
            prompt_client, "post", return_value=expected_response
        ) as mock_post:
            result = prompt_client.get_traces(sample_traces_dto)

            assert result == expected_response
            mock_post.assert_called_once_with(
                "prompts/get-traces", json=sample_traces_dto
            )

    def test_get_traces_error(self, prompt_client, sample_traces_dto):
        """Test get traces with error"""
        with patch.object(
            prompt_client, "post", side_effect=httpx.RequestError("Connection failed")
        ):
            with pytest.raises(ModelHubAPIException) as exc_info:
                prompt_client.get_traces(sample_traces_dto)

            assert "error in getting traces" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_aget_traces_success(self, prompt_client, sample_traces_dto):
        """Test successful async get traces"""
        expected_response = {"traces": [{"id": "trace-1"}, {"id": "trace-2"}]}

        with patch.object(
            prompt_client, "apost", return_value=expected_response
        ) as mock_apost:
            result = await prompt_client.aget_traces(sample_traces_dto)

            assert result == expected_response
            mock_apost.assert_called_once_with(
                "prompts/get-traces", json=sample_traces_dto
            )

    @pytest.mark.asyncio
    async def test_aget_traces_error(self, prompt_client, sample_traces_dto):
        """Test async get traces with error"""
        with patch.object(
            prompt_client, "apost", side_effect=httpx.RequestError("Connection failed")
        ):
            with pytest.raises(ModelHubAPIException) as exc_info:
                await prompt_client.aget_traces(sample_traces_dto)

            assert "error in getting traces" in str(exc_info.value)

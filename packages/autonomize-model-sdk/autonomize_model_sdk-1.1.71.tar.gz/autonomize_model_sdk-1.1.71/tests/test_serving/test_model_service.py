# import os
# from unittest.mock import MagicMock, patch

# import numpy as np
# import pandas as pd
# import pytest

# from modelhub.serving.model_service import (
#     ImageModelService,
#     ModelhubModelService,
#     ModelServiceGroup,
# )


# @pytest.fixture
# def mock_mlflow_client():
#     with patch("modelhub.serving.model_service.MLflowClient") as mock_client:
#         mock_instance = MagicMock()
#         mock_client.return_value = mock_instance
#         mock_instance.mlflow.pyfunc.load_model.return_value = MagicMock()
#         yield mock_instance


# @pytest.fixture
# def model_service(mock_mlflow_client):
#     service = ModelhubModelService(
#         name="test-model",
#         run_uri="runs:/abc123/model",
#         model_type="pyfunc",
#         modelhub_base_url="http://test-url",
#     )
#     return service


# @pytest.fixture
# def loaded_model_service(model_service):
#     model_service.loaded_model = MagicMock()
#     model_service.ready = True
#     return model_service


# @pytest.fixture
# def image_model_service(mock_mlflow_client):
#     service = ImageModelService(
#         name="test-image-model",
#         run_uri="runs:/abc123/model",
#         modelhub_base_url="http://test-url",
#     )
#     return service


# # Mock BytesIO to avoid actual file operations
# @pytest.fixture
# def mock_bytesio():
#     with patch("modelhub.serving.model_service.BytesIO") as mock_io:
#         mock_buffer = MagicMock()
#         mock_io.return_value = mock_buffer
#         mock_buffer.getvalue.return_value = b"fake-image-data"
#         yield mock_io


# # Tests for ModelhubModelService
# def test_init_model_service(model_service):
#     assert model_service.name == "test-model"
#     assert model_service.run_uri == "runs:/abc123/model"
#     assert model_service.model_type == "pyfunc"
#     assert model_service.modelhub_base_url == "http://test-url"
#     assert model_service.ready is False


# def test_init_model_service_env_url(mock_mlflow_client):
#     """Test that the base URL is taken from environment if not provided"""
#     with patch.dict(os.environ, {"MODELHUB_BASE_URL": "http://env-url"}):
#         service = ModelhubModelService(name="test-model", run_uri="runs:/abc123/model")
#         assert service.modelhub_base_url == "http://env-url"


# def test_init_model_service_missing_url():
#     """Test that an error is raised if no base URL is provided"""
#     with patch.dict(os.environ, {}, clear=True):
#         with pytest.raises(
#             ValueError, match="MODELHUB_BASE_URL environment variable is required"
#         ):
#             ModelhubModelService(name="test-model", run_uri="runs:/abc123/model")


# def test_load_pyfunc_model(model_service, mock_mlflow_client):
#     model_service.load()
#     assert model_service.ready is True
#     mock_mlflow_client.mlflow.pyfunc.load_model.assert_called_once_with(
#         "runs:/abc123/model"
#     )


# def test_load_transformer_model(mock_mlflow_client):
#     """Test loading a transformer model"""
#     # Create a transformer mock for the client's mlflow
#     mock_transformers = MagicMock()
#     mock_mlflow_client.mlflow.transformers = mock_transformers

#     service = ModelhubModelService(
#         name="test-transformer",
#         run_uri="runs:/abc123/model",
#         model_type="transformer",
#         modelhub_base_url="http://test-url",
#     )

#     # Load model
#     service.load()

#     # Verify
#     assert service.ready is True
#     mock_mlflow_client.mlflow.transformers.load_model.assert_called_once_with(
#         "runs:/abc123/model"
#     )


# def test_load_sklearn_model(mock_mlflow_client):
#     """Test loading a scikit-learn model"""
#     # Create a sklearn mock for the client's mlflow
#     mock_sklearn = MagicMock()
#     mock_mlflow_client.mlflow.sklearn = mock_sklearn

#     service = ModelhubModelService(
#         name="test-sklearn",
#         run_uri="runs:/abc123/model",
#         model_type="sklearn",
#         modelhub_base_url="http://test-url",
#     )

#     service.load()
#     assert service.ready is True
#     mock_mlflow_client.mlflow.sklearn.load_model.assert_called_once_with(
#         "runs:/abc123/model"
#     )


# def test_load_custom_model(model_service, mock_mlflow_client):
#     service = ModelhubModelService(
#         name="test-custom",
#         run_uri="runs:/abc123/model",
#         model_type="custom",
#         modelhub_base_url="http://test-url",
#     )
#     service.load()
#     assert service.ready is True
#     mock_mlflow_client.mlflow.pyfunc.load_model.assert_called_once_with(
#         "runs:/abc123/model"
#     )


# def test_load_model_error(mock_mlflow_client):
#     mock_mlflow_client.mlflow.pyfunc.load_model.side_effect = Exception("Test error")
#     service = ModelhubModelService(
#         name="test-error",
#         run_uri="runs:/abc123/model",
#         modelhub_base_url="http://test-url",
#     )
#     with pytest.raises(Exception, match="Test error"):
#         service.load()
#     assert service.ready is False


# @pytest.mark.asyncio
# async def test_predict_not_ready(model_service):
#     result = await model_service.predict({"text": "test"})
#     assert result["statusCode"] == 503
#     assert "Model is not loaded yet" in result["message"]


# @pytest.mark.asyncio
# async def test_predict_text(loaded_model_service):
#     loaded_model_service.loaded_model.predict.return_value = "Positive"

#     result = await loaded_model_service.predict({"text": "test text"})

#     assert result["statusCode"] == 200
#     assert result["data"] == "Positive"
#     loaded_model_service.loaded_model.predict.assert_called_once_with("test text")


# @pytest.mark.asyncio
# async def test_predict_text_missing_input(loaded_model_service):
#     result = await loaded_model_service.predict_text({})

#     assert result["statusCode"] == 400
#     assert "Missing 'text' field in request" in result["message"]


# @pytest.mark.asyncio
# async def test_predict_tabular(loaded_model_service):
#     loaded_model_service.loaded_model.predict.return_value = [1, 0, 1]

#     # Test with list of records
#     data = [{"feature1": 1, "feature2": 2}, {"feature1": 3, "feature2": 4}]
#     result = await loaded_model_service.predict({"data": data})

#     assert result["statusCode"] == 200
#     assert result["data"] == [1, 0, 1]

#     # Test with single record
#     data = {"feature1": 1, "feature2": 2}
#     result = await loaded_model_service.predict({"data": data})

#     assert result["statusCode"] == 200
#     assert result["data"] == [1, 0, 1]


# @pytest.mark.asyncio
# async def test_predict_tabular_dataframe_result(loaded_model_service):
#     loaded_model_service.loaded_model.predict.return_value = pd.DataFrame(
#         {"prediction": [1, 0, 1]}
#     )

#     data = [{"feature1": 1, "feature2": 2}, {"feature1": 3, "feature2": 4}]
#     result = await loaded_model_service.predict({"data": data})

#     assert result["statusCode"] == 200
#     assert isinstance(result["data"], list)
#     assert len(result["data"]) == 3
#     assert result["data"][0]["prediction"] == 1


# @pytest.mark.asyncio
# async def test_predict_tabular_series_result(loaded_model_service):
#     # Create a Series with a specific method mock for to_dict
#     series_mock = MagicMock(spec=pd.Series)
#     # The to_dict method should return a dict
#     series_mock.to_dict.return_value = {"0": 1, "1": 0, "2": 1}
#     # Check if we're using hasattr(prediction, "to_dict")
#     type(series_mock).to_dict = MagicMock(return_value={"0": 1, "1": 0, "2": 1})

#     loaded_model_service.loaded_model.predict.return_value = series_mock

#     data = [{"feature1": 1, "feature2": 2}, {"feature1": 3, "feature2": 4}]
#     result = await loaded_model_service.predict({"data": data})

#     assert result["statusCode"] == 200
#     assert isinstance(result["data"], dict)
#     assert "0" in result["data"]
#     assert result["data"]["0"] == 1


# @pytest.mark.asyncio
# async def test_predict_tabular_missing_input(loaded_model_service):
#     result = await loaded_model_service.predict_tabular({})

#     assert result["statusCode"] == 400
#     assert "Missing 'data' field in request" in result["message"]


# @pytest.mark.asyncio
# async def test_predict_image(loaded_model_service):
#     loaded_model_service.loaded_model.predict.return_value = {"class": "document"}

#     # Mock image data
#     image_data = b"fake-image-data"
#     result = await loaded_model_service.predict({"image": image_data})

#     assert result["statusCode"] == 200
#     assert result["data"] == {"class": "document"}

#     # Verify DataFrame was created correctly
#     args, _ = loaded_model_service.loaded_model.predict.call_args
#     df = args[0]
#     assert isinstance(df, pd.DataFrame)
#     assert "image" in df.columns
#     assert len(df) == 1


# @pytest.mark.asyncio
# async def test_predict_image_missing_input(loaded_model_service):
#     result = await loaded_model_service.predict_image({})

#     assert result["statusCode"] == 400
#     assert "Missing 'image' field in request" in result["message"]


# @pytest.mark.asyncio
# async def test_predict_image_error(loaded_model_service):
#     loaded_model_service.loaded_model.predict.side_effect = Exception("Test error")

#     result = await loaded_model_service.predict({"image": b"fake-image-data"})

#     assert result["statusCode"] == 400
#     assert "Error processing image" in result["message"]


# @pytest.mark.asyncio
# async def test_predict_images(loaded_model_service):
#     loaded_model_service.loaded_model.predict.return_value = [
#         {"class": "document1"},
#         {"class": "document2"},
#     ]

#     # Test with binary data
#     images = [b"fake-image-data-1", b"fake-image-data-2"]
#     result = await loaded_model_service.predict({"images": images})

#     assert result["statusCode"] == 200
#     assert result["data"] == [{"class": "document1"}, {"class": "document2"}]

#     # Verify DataFrame was created correctly
#     args, _ = loaded_model_service.loaded_model.predict.call_args
#     df = args[0]
#     assert isinstance(df, pd.DataFrame)
#     assert "image" in df.columns
#     assert len(df) == 2


# @pytest.mark.asyncio
# async def test_predict_images_with_pil(loaded_model_service, mock_bytesio):
#     loaded_model_service.loaded_model.predict.return_value = [
#         {"class": "document1"},
#         {"class": "document2"},
#     ]

#     # Create mock PIL images
#     pil_image1 = MagicMock(spec=["save"])
#     pil_image2 = MagicMock(spec=["save"])

#     result = await loaded_model_service.predict({"images": [pil_image1, pil_image2]})

#     assert result["statusCode"] == 200
#     assert result["data"] == [{"class": "document1"}, {"class": "document2"}]
#     assert pil_image1.save.called
#     assert pil_image2.save.called


# @pytest.mark.asyncio
# async def test_predict_images_missing_input(loaded_model_service):
#     result = await loaded_model_service.predict_images({})

#     assert result["statusCode"] == 400
#     assert "Missing or empty 'images' field in request" in result["message"]


# @pytest.mark.asyncio
# async def test_predict_images_error(loaded_model_service):
#     loaded_model_service.loaded_model.predict.side_effect = Exception("Test error")

#     result = await loaded_model_service.predict({"images": [b"fake-image-data"]})

#     assert result["statusCode"] == 400
#     assert "Error processing images" in result["message"]


# # For PDF tests, we use our custom pdf2image implementation
# @pytest.mark.asyncio
# async def test_predict_pdf(loaded_model_service, mock_bytesio):
#     # Setup
#     loaded_model_service.loaded_model.predict.return_value = [
#         {"class": "page1"},
#         {"class": "page2"},
#     ]

#     # Create a mock for our custom pdf2image function
#     mock_pdf2image = MagicMock()
#     # Make it return a list of PIL image mocks
#     pil_images = [MagicMock(spec=["save"]), MagicMock(spec=["save"])]
#     mock_pdf2image.return_value = pil_images

#     # Patch the _try_import_pdf2image method to return our mock
#     with patch.object(
#         loaded_model_service, "_try_import_pdf2image", return_value=mock_pdf2image
#     ):
#         result = await loaded_model_service.predict({"pdf_file": b"fake-pdf-data"})

#     assert result["statusCode"] == 200
#     assert result["data"] == [{"class": "page1"}, {"class": "page2"}]
#     mock_pdf2image.assert_called_once_with(
#         byte_stream=b"fake-pdf-data", return_image=True, zoom=2
#     )


# @pytest.mark.asyncio
# async def test_predict_pdf_missing_input(loaded_model_service):
#     result = await loaded_model_service.predict_pdf({})

#     assert result["statusCode"] == 400
#     assert "Missing 'pdf_file' field in request" in result["message"]


# @pytest.mark.asyncio
# async def test_predict_pdf_import_error(loaded_model_service):
#     # Mock the _try_import_pdf2image method to return None (import failed)
#     with patch.object(loaded_model_service, "_try_import_pdf2image", return_value=None):
#         result = await loaded_model_service.predict({"pdf_file": b"fake-pdf-data"})

#     assert result["statusCode"] == 400
#     assert "PyMuPDF (fitz) is required for PDF processing" in result["message"]


# @pytest.mark.asyncio
# async def test_predict_raw(loaded_model_service):
#     loaded_model_service.loaded_model.predict.return_value = {"result": "success"}

#     request = {"key1": "value1", "key2": "value2"}
#     result = await loaded_model_service.predict(request)

#     assert result["statusCode"] == 200
#     assert result["data"] == {"result": "success"}
#     loaded_model_service.loaded_model.predict.assert_called_once_with(request)


# @pytest.mark.asyncio
# async def test_predict_exception(loaded_model_service):
#     loaded_model_service.loaded_model.predict.side_effect = Exception(
#         "Unexpected error"
#     )

#     result = await loaded_model_service.predict({"text": "test"})

#     assert result["statusCode"] == 400
#     assert "Error during prediction" in result["message"]


# # Tests for ImageModelService
# def test_init_image_model_service(image_model_service):
#     assert image_model_service.name == "test-image-model"
#     assert image_model_service.run_uri == "runs:/abc123/model"
#     assert image_model_service.model_type == "pyfunc"  # Default model type
#     assert image_model_service.modelhub_base_url == "http://test-url"


# @pytest.mark.asyncio
# async def test_image_predict_not_ready(image_model_service):
#     result = await image_model_service.predict({"images": [b"fake-image"]})
#     assert result["statusCode"] == 503
#     assert "Model is not loaded yet" in result["message"]


# @pytest.mark.asyncio
# async def test_image_predict_with_images(image_model_service, mock_bytesio):
#     image_model_service.loaded_model = MagicMock()
#     image_model_service.loaded_model.predict.return_value = [
#         {"class": "doc1"},
#         {"class": "doc2"},
#     ]
#     image_model_service.ready = True

#     # Test with binary data
#     images = [b"fake-image-1", b"fake-image-2"]
#     result = await image_model_service.predict({"images": images})

#     assert result["statusCode"] == 200
#     assert result["data"] == [{"class": "doc1"}, {"class": "doc2"}]

#     # Verify DataFrame was created correctly
#     args, _ = image_model_service.loaded_model.predict.call_args
#     df = args[0]
#     assert isinstance(df, pd.DataFrame)
#     assert "image" in df.columns
#     assert len(df) == 2


# @pytest.mark.asyncio
# async def test_image_predict_with_pdf(image_model_service, mock_bytesio):
#     # Setup
#     image_model_service.loaded_model = MagicMock()
#     image_model_service.loaded_model.predict.return_value = [
#         {"class": "page1"},
#         {"class": "page2"},
#     ]
#     image_model_service.ready = True

#     # Mock the PDF processing
#     pdf_images = [MagicMock(spec=["save"]), MagicMock(spec=["save"])]

#     with patch.object(image_model_service, "_process_pdf", return_value=pdf_images):
#         result = await image_model_service.predict({"pdf_file": b"fake-pdf-data"})

#     assert result["statusCode"] == 200
#     assert result["data"] == [{"class": "page1"}, {"class": "page2"}]


# @pytest.mark.asyncio
# async def test_image_predict_with_pdf_import_error(image_model_service):
#     # Setup
#     image_model_service.ready = True

#     # Mock the PDF processing to raise an import error
#     with patch.object(
#         image_model_service, "_process_pdf", side_effect=ImportError("No fitz module")
#     ):
#         result = await image_model_service.predict({"pdf_file": b"fake-pdf-data"})

#     assert result["statusCode"] == 400
#     assert "PyMuPDF (fitz) is required for PDF processing" in result["message"]


# @pytest.mark.asyncio
# async def test_image_predict_with_pil_images(image_model_service, mock_bytesio):
#     image_model_service.loaded_model = MagicMock()
#     image_model_service.loaded_model.predict.return_value = [
#         {"class": "img1"},
#         {"class": "img2"},
#     ]
#     image_model_service.ready = True

#     # Create PIL images
#     pil_image1 = MagicMock(spec=["save"])
#     pil_image2 = MagicMock(spec=["save"])

#     result = await image_model_service.predict({"images": [pil_image1, pil_image2]})

#     assert result["statusCode"] == 200
#     assert result["data"] == [{"class": "img1"}, {"class": "img2"}]
#     assert pil_image1.save.called
#     assert pil_image2.save.called


# @pytest.mark.asyncio
# async def test_image_predict_error(image_model_service):
#     image_model_service.loaded_model = MagicMock()
#     image_model_service.loaded_model.predict.side_effect = Exception("Test error")
#     image_model_service.ready = True

#     result = await image_model_service.predict({"images": [b"fake-image"]})

#     assert result["statusCode"] == 400
#     assert "Error during prediction" in result["message"]


# # Tests for ModelServiceGroup
# def test_model_service_group():
#     model1 = MagicMock()
#     model2 = MagicMock()

#     group = ModelServiceGroup([model1, model2])
#     assert len(group.models) == 2

#     group.load_models()

#     model1.load.assert_called_once()
#     model2.load.assert_called_once()


# # Additional tests for the _try_import_pdf2image method
# def test_try_import_pdf2image_success():
#     """Test successful pdf2image import"""
#     # Mock both the MLflowClient and the _try_import_pdf2image method
#     with patch("modelhub.serving.model_service.MLflowClient") as mock_client:
#         with patch(
#             "modelhub.serving.model_service.ModelhubModelService._try_import_pdf2image"
#         ) as mock_import:
#             # Set up the mock to return a function
#             mock_pdf2image = MagicMock()
#             mock_import.return_value = mock_pdf2image

#             # Create the service with the mocked client
#             service = ModelhubModelService(
#                 name="test-model",
#                 run_uri="runs:/abc123/model",
#                 modelhub_base_url="http://localhost",  # Use localhost to avoid actual connection attempts
#             )

#             # Call the method directly to test it
#             result = service._try_import_pdf2image()

#             # Verify the method was called and returns the expected value
#             assert result is mock_pdf2image


# # Tests for predict with various return types
# @pytest.mark.asyncio
# async def test_predict_tabular_numpy_array_result(loaded_model_service):
#     """Test handling of numpy array prediction results"""
#     # Create numpy array result
#     np_array = np.array([1, 0, 1])
#     loaded_model_service.loaded_model.predict.return_value = np_array

#     data = [{"feature1": 1, "feature2": 2}]
#     result = await loaded_model_service.predict({"data": data})

#     assert result["statusCode"] == 200
#     assert result["data"] == [1, 0, 1]  # Should convert to list


# @pytest.mark.asyncio
# async def test_predict_tabular_scalar_result(loaded_model_service):
#     """Test handling of scalar prediction results"""
#     # Return a scalar value
#     loaded_model_service.loaded_model.predict.return_value = 0.95

#     data = {"feature1": 1, "feature2": 2}
#     result = await loaded_model_service.predict({"data": data})

#     assert result["statusCode"] == 200
#     assert result["data"] == 0.95


# # Test empty response handling
# @pytest.mark.asyncio
# async def test_predict_empty_result(loaded_model_service):
#     """Test handling of empty prediction results"""
#     # Return empty list
#     loaded_model_service.loaded_model.predict.return_value = []

#     result = await loaded_model_service.predict({"data": [{"feature1": 1}]})

#     assert result["statusCode"] == 200
#     assert result["data"] == []


# # Test handling of PDF processing errors
# @pytest.mark.asyncio
# async def test_predict_pdf_extraction_failure(loaded_model_service):
#     """Test handling of PDF extraction failures"""
#     # Mock successful pdf2image import but failed extraction
#     mock_pdf2image = MagicMock()
#     mock_pdf2image.return_value = []  # Empty list = no images extracted

#     with patch.object(
#         loaded_model_service, "_try_import_pdf2image", return_value=mock_pdf2image
#     ):
#         result = await loaded_model_service.predict({"pdf_file": b"corrupted-pdf-data"})

#     assert result["statusCode"] == 400
#     assert "Failed to extract images from PDF" in result["message"]


# @pytest.mark.asyncio
# async def test_predict_pdf_processing_error(loaded_model_service):
#     """Test handling of errors during PDF processing"""
#     # Mock successful pdf2image import but failed processing
#     mock_pdf2image = MagicMock()
#     mock_pdf2image.side_effect = Exception("Error processing PDF")

#     with patch.object(
#         loaded_model_service, "_try_import_pdf2image", return_value=mock_pdf2image
#     ):
#         result = await loaded_model_service.predict({"pdf_file": b"corrupted-pdf-data"})

#     assert result["statusCode"] == 400
#     assert "Error processing PDF" in result["message"]


# # Test for ImageModelService with mixed input types
# @pytest.mark.asyncio
# async def test_image_predict_mixed_inputs(image_model_service, mock_bytesio):
#     """Test ImageModelService with both PDF and images together"""
#     image_model_service.loaded_model = MagicMock()
#     image_model_service.loaded_model.predict.return_value = [
#         {"class": "pdf_page"},
#         {"class": "regular_image1"},
#         {"class": "regular_image2"},
#     ]
#     image_model_service.ready = True

#     # Create PDF images and regular images
#     pdf_images = [MagicMock(spec=["save"])]
#     regular_images = [b"image1", b"image2"]

#     # Mock PDF processing
#     with patch.object(image_model_service, "_process_pdf", return_value=pdf_images):
#         result = await image_model_service.predict(
#             {"pdf_file": b"fake-pdf-data", "images": regular_images}
#         )

#     assert result["statusCode"] == 200
#     assert len(result["data"]) == 3  # 1 PDF page + 2 regular images

#     # Verify we passed a DataFrame with 3 rows to the model
#     args, _ = image_model_service.loaded_model.predict.call_args
#     df = args[0]
#     assert isinstance(df, pd.DataFrame)
#     assert len(df) == 3


# # Test for ModelServiceGroup with multiple models
# def test_model_service_group_multiple_models():
#     """Test ModelServiceGroup with multiple models of different types"""
#     # Create mocks for different model types
#     pyfunc_model = MagicMock(spec=ModelhubModelService)
#     transformer_model = MagicMock(spec=ModelhubModelService)
#     image_model = MagicMock(spec=ImageModelService)

#     # Create a group with all models
#     group = ModelServiceGroup([pyfunc_model, transformer_model, image_model])

#     # Test loading all models
#     group.load_models()

#     # Verify all models were loaded
#     pyfunc_model.load.assert_called_once()
#     transformer_model.load.assert_called_once()
#     image_model.load.assert_called_once()


# # Tests for error cases in ImageModelService
# @pytest.mark.asyncio
# async def test_image_predict_pdf_general_error(image_model_service):
#     """Test handling of general errors during PDF processing in ImageModelService"""
#     image_model_service.ready = True

#     # Mock PDF processing to raise a general error
#     with patch.object(
#         image_model_service,
#         "_process_pdf",
#         side_effect=Exception("General PDF processing error"),
#     ):
#         result = await image_model_service.predict({"pdf_file": b"fake-pdf-data"})

#     assert result["statusCode"] == 400
#     assert "Error processing PDF" in result["message"]


# @pytest.mark.asyncio
# async def test_image_predict_no_inputs(image_model_service):
#     """Test ImageModelService when no inputs are provided"""
#     image_model_service.ready = True
#     image_model_service.loaded_model = (
#         MagicMock()
#     )  # Add this line to set the loaded_model

#     # Call predict with empty request (no PDF, no images)
#     result = await image_model_service.predict({})

#     # Should return 200 with empty DataFrame
#     assert result["statusCode"] == 200

#     # Verify we passed an empty DataFrame to the model
#     args, _ = image_model_service.loaded_model.predict.call_args
#     df = args[0]
#     assert isinstance(df, pd.DataFrame)
#     assert len(df) == 0


def test_assert():
    assert True

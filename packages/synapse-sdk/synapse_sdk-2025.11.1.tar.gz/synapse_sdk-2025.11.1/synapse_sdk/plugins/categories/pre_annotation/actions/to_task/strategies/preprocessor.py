"""Pre-processor management strategies for ToTask action."""

from typing import Any, Dict

from .base import PreProcessorStrategy, ToTaskContext


class PreProcessorManagementStrategy(PreProcessorStrategy):
    """Strategy for managing pre-processor lifecycle."""

    def get_preprocessor_info(self, context: ToTaskContext, preprocessor_id: int) -> Dict[str, Any]:
        """Get pre-processor information from the backend.

        Args:
            context: Shared context for the action execution
            preprocessor_id: The pre-processor ID

        Returns:
            Dict with pre-processor info or error
        """
        try:
            client = context.client
            pre_processor_response = client.get_plugin_release(preprocessor_id)
            if isinstance(pre_processor_response, str):
                return {'success': False, 'error': 'Invalid pre-processor response received'}

            pre_processor: Dict[str, Any] = pre_processor_response
            config = pre_processor.get('config', {})
            code = config.get('code')
            version = pre_processor.get('version')

            if not code or not version:
                return {'success': False, 'error': 'Invalid pre-processor configuration'}

            return {'success': True, 'code': code, 'version': version}
        except Exception as e:
            return {'success': False, 'error': f'Failed to get pre-processor info: {str(e)}'}

    def ensure_preprocessor_running(self, context: ToTaskContext, preprocessor_code: str) -> Dict[str, Any]:
        """Ensure the pre-processor is running, restart if necessary.

        Args:
            context: Shared context for the action execution
            preprocessor_code: The pre-processor code

        Returns:
            Dict indicating success or failure
        """
        try:
            client = context.client

            # Check if pre-processor is running
            serve_applications_response = client.list_serve_applications(params={'plugin_code': preprocessor_code})
            if isinstance(serve_applications_response, str):
                return {'success': False, 'error': 'Invalid serve applications response'}

            # Handle the response properly - it should be a dict with 'results' key
            if not isinstance(serve_applications_response, dict):
                return {'success': False, 'error': 'Unexpected serve applications response format'}

            serve_applications: Dict[str, Any] = serve_applications_response
            results = serve_applications.get('results', [])
            running_serve_apps = [app for app in results if isinstance(app, dict) and app.get('status') == 'RUNNING']

            # If not running, restart the pre-processor
            if not running_serve_apps:
                restart_result = self._restart_preprocessor(context, preprocessor_code)
                if not restart_result['success']:
                    return restart_result

                # Verify restart was successful
                serve_applications_response = client.list_serve_applications(params={'plugin_code': preprocessor_code})
                if isinstance(serve_applications_response, str):
                    return {'success': False, 'error': 'Failed to verify pre-processor restart'}

                serve_applications = serve_applications_response
                results = serve_applications.get('results', [])
                running_serve_apps = [
                    app for app in results if isinstance(app, dict) and app.get('status') == 'RUNNING'
                ]

                if not running_serve_apps:
                    return {'success': False, 'error': 'Pre-processor failed to start after restart'}

            return {'success': True}

        except Exception as e:
            return {'success': False, 'error': f'Failed to ensure pre-processor running: {str(e)}'}

    def _restart_preprocessor(self, context: ToTaskContext, preprocessor_code: str) -> Dict[str, Any]:
        """Restart the pre-processor.

        Args:
            context: Shared context for the action execution
            preprocessor_code: The pre-processor code

        Returns:
            Dict indicating success or failure
        """
        try:
            client = context.client

            # Start the serve application
            inference_options = context.config.get('inference_options', {})
            serve_application_deployment_payload = {
                'agent': context.params.get('agent') if context.params else None,
                'action': 'deployment',
                'params': {
                    'num_cpus': inference_options.get('required_cpu_count', 2),
                    'num_gpus': inference_options.get('required_gpu_count', 1),
                },
                'debug': True,
            }

            deployment_result = client.run_plugin(
                preprocessor_code,
                serve_application_deployment_payload,
            )

            deployment_job_id = deployment_result.get('job_id')
            if not deployment_job_id:
                return {'success': False, 'error': 'No deployment job ID returned'}

            return {'success': True, 'error': 'Pre-processor restarted successfully'}

        except Exception as e:
            return {'success': False, 'error': f'Failed to restart pre-processor: {str(e)}'}

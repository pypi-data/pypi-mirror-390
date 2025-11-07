"""
Tests for WorkflowGuide
"""

import pytest
from fakemcp.database import Database
from fakemcp.workflow_guide import WorkflowGuide
from fakemcp.models import WorkflowState


@pytest.fixture
def db():
    """Create a test database"""
    database = Database(":memory:")
    yield database
    database.close()


@pytest.fixture
def workflow_guide(db):
    """Create a WorkflowGuide instance"""
    return WorkflowGuide(db)


class TestWorkflowGuide:
    """Test WorkflowGuide functionality"""

    def test_start_workflow(self, workflow_guide):
        """Test starting a new workflow"""
        state = workflow_guide.start_workflow()
        
        assert state is not None
        assert state.stage == WorkflowGuide.STAGE_INIT
        assert isinstance(state.data, dict)
        assert isinstance(state.history, list)
        assert len(state.history) == 1
        assert state.history[0]['event_type'] == 'workflow_started'

    def test_get_current_state(self, workflow_guide):
        """Test getting current workflow state"""
        # Initially no state
        state = workflow_guide.get_current_state()
        assert state is None
        
        # After starting workflow
        workflow_guide.start_workflow()
        state = workflow_guide.get_current_state()
        assert state is not None
        assert state.stage == WorkflowGuide.STAGE_INIT

    def test_advance_stage(self, workflow_guide):
        """Test advancing to next stage"""
        workflow_guide.start_workflow()
        
        # Advance from init to target_collection
        state = workflow_guide.advance_stage()
        assert state.stage == WorkflowGuide.STAGE_TARGET_COLLECTION
        
        # Advance to actor_analysis
        state = workflow_guide.advance_stage()
        assert state.stage == WorkflowGuide.STAGE_ACTOR_ANALYSIS
        
        # Check history
        assert len(state.history) >= 3  # start + 2 advances

    def test_advance_stage_with_data_updates(self, workflow_guide):
        """Test advancing stage with data updates"""
        workflow_guide.start_workflow()
        
        updates = {'scenario_id': 'test_scenario', 'target_mcps': ['mcp1', 'mcp2']}
        state = workflow_guide.advance_stage(data_updates=updates)
        
        assert state.stage == WorkflowGuide.STAGE_TARGET_COLLECTION
        assert state.data['scenario_id'] == 'test_scenario'
        assert state.data['target_mcps'] == ['mcp1', 'mcp2']

    def test_advance_stage_at_completion(self, workflow_guide):
        """Test that advancing at completed stage doesn't change stage"""
        workflow_guide.start_workflow()
        
        # Advance to completed stage
        for _ in range(len(WorkflowGuide.STAGE_ORDER) - 1):
            workflow_guide.advance_stage()
        
        state = workflow_guide.get_current_state()
        assert state.stage == WorkflowGuide.STAGE_COMPLETED
        
        # Try to advance further
        state = workflow_guide.advance_stage()
        assert state.stage == WorkflowGuide.STAGE_COMPLETED

    def test_update_data(self, workflow_guide):
        """Test updating workflow data"""
        workflow_guide.start_workflow()
        
        updates = {
            'scenario_description': 'Memory leak scenario',
            'actors': ['server-01', 'server-02']
        }
        state = workflow_guide.update_data(updates)
        
        assert state.data['scenario_description'] == 'Memory leak scenario'
        assert state.data['actors'] == ['server-01', 'server-02']

    def test_add_plot_suggestion(self, workflow_guide):
        """Test adding plot suggestions"""
        workflow_guide.start_workflow()
        
        suggestion = {
            'type': 'root_cause',
            'description': 'Database connection pool not released',
            'actors': ['database-01', 'server-01']
        }
        
        state = workflow_guide.add_plot_suggestion(suggestion)
        
        assert len(state.plot_suggestions) == 1
        assert state.plot_suggestions[0]['type'] == 'root_cause'

    def test_reset_workflow(self, workflow_guide):
        """Test resetting workflow"""
        workflow_guide.start_workflow()
        workflow_guide.update_data({'test': 'data'})
        workflow_guide.advance_stage()
        
        # Reset
        workflow_guide.reset_workflow()
        
        state = workflow_guide.get_current_state()
        assert state is None

    def test_get_progress(self, workflow_guide):
        """Test progress calculation"""
        # No workflow
        progress = workflow_guide.get_progress()
        assert progress == 0
        
        # Start workflow (init stage)
        workflow_guide.start_workflow()
        progress = workflow_guide.get_progress()
        assert progress == 0
        
        # Advance to middle stage
        for _ in range(4):  # Advance to plot_deepening
            workflow_guide.advance_stage()
        
        progress = workflow_guide.get_progress()
        assert 30 < progress < 70  # Should be somewhere in the middle
        
        # Advance to completed
        while workflow_guide.get_current_state().stage != WorkflowGuide.STAGE_COMPLETED:
            workflow_guide.advance_stage()
        
        progress = workflow_guide.get_progress()
        assert progress == 100

    def test_generate_prompt_start(self, workflow_guide):
        """Test generating prompt with 'start' action"""
        result = workflow_guide.generate_prompt(action='start')
        
        assert result['stage'] == WorkflowGuide.STAGE_INIT
        assert 'prompt' in result
        assert 'nextActions' in result
        assert 'progress' in result
        assert result['progress'] == 0

    def test_generate_prompt_next(self, workflow_guide):
        """Test generating prompt with 'next' action"""
        workflow_guide.start_workflow()
        
        result = workflow_guide.generate_prompt(action='next')
        
        assert result['stage'] == WorkflowGuide.STAGE_INIT
        assert isinstance(result['prompt'], str)
        assert len(result['prompt']) > 0

    def test_generate_prompt_status(self, workflow_guide):
        """Test generating status response"""
        workflow_guide.start_workflow()
        workflow_guide.update_data({'test_key': 'test_value'})
        
        result = workflow_guide.generate_prompt(action='status')
        
        assert result['stage'] == WorkflowGuide.STAGE_INIT
        assert 'data' in result
        assert result['data']['test_key'] == 'test_value'
        assert 'history' in result

    def test_generate_prompt_reset(self, workflow_guide):
        """Test generating prompt with 'reset' action"""
        workflow_guide.start_workflow()
        workflow_guide.advance_stage()
        
        result = workflow_guide.generate_prompt(action='reset')
        
        # Should reset and start new workflow
        assert result['stage'] == WorkflowGuide.STAGE_INIT
        assert result['progress'] == 0

    def test_generate_init_prompt(self, workflow_guide):
        """Test init stage prompt generation"""
        workflow_guide.start_workflow()
        
        result = workflow_guide.generate_prompt()
        
        assert 'set_scenario' in result['nextActions']
        assert 'add_target_mcp' in result['nextActions']
        assert '场景' in result['prompt'] or 'scenario' in result['prompt'].lower()

    def test_generate_target_collection_prompt(self, workflow_guide):
        """Test target collection stage prompt generation"""
        workflow_guide.start_workflow()
        workflow_guide.advance_stage()
        workflow_guide.update_data({
            'target_mcps': ['prometheus', 'cloudmonitoring'],
            'actor_fields': {
                'prometheus': ['instance', 'job'],
                'cloudmonitoring': ['resource_id']
            }
        })
        
        result = workflow_guide.generate_prompt()
        
        assert result['stage'] == WorkflowGuide.STAGE_TARGET_COLLECTION
        assert 'fetch_real_data' in result['nextActions']
        assert 'prometheus' in result['prompt']

    def test_generate_actor_analysis_prompt(self, workflow_guide):
        """Test actor analysis stage prompt generation"""
        workflow_guide.start_workflow()
        workflow_guide.advance_stage()  # target_collection
        workflow_guide.advance_stage()  # actor_analysis
        workflow_guide.update_data({
            'scenario_description': 'Memory leak scenario',
            'actor_fields': {'prometheus': ['server_id']}
        })
        
        result = workflow_guide.generate_prompt()
        
        assert result['stage'] == WorkflowGuide.STAGE_ACTOR_ANALYSIS
        assert 'add_actor_config' in result['nextActions']
        assert 'Memory leak scenario' in result['prompt']

    def test_generate_plot_deepening_prompt(self, workflow_guide):
        """Test plot deepening stage prompt generation"""
        workflow_guide.start_workflow()
        for _ in range(3):  # Advance to plot_deepening
            workflow_guide.advance_stage()
        
        workflow_guide.update_data({
            'actors': ['server-01', 'server-02'],
            'target_mcps': ['prometheus', 'logging'],
            'main_event': 'memory leak'
        })
        
        result = workflow_guide.generate_prompt()
        
        assert result['stage'] == WorkflowGuide.STAGE_PLOT_DEEPENING
        assert 'request_plot_expansion' in result['nextActions']
        assert 'add_causality_relation' in result['nextActions']
        assert 'memory leak' in result['prompt']

    def test_generate_scenario_creation_prompt(self, workflow_guide):
        """Test scenario creation stage prompt generation"""
        workflow_guide.start_workflow()
        for _ in range(4):  # Advance to scenario_creation
            workflow_guide.advance_stage()
        
        workflow_guide.update_data({'causality_relations_count': 3})
        
        result = workflow_guide.generate_prompt()
        
        assert result['stage'] == WorkflowGuide.STAGE_SCENARIO_CREATION
        assert 'build_plot_graph' in result['nextActions']
        assert 'validate_plot_consistency' in result['nextActions']
        assert '3' in result['prompt']

    def test_generate_data_generation_prompt(self, workflow_guide):
        """Test data generation stage prompt generation"""
        workflow_guide.start_workflow()
        for _ in range(5):  # Advance to data_generation
            workflow_guide.advance_stage()
        
        workflow_guide.update_data({'plot_nodes_count': 5})
        
        result = workflow_guide.generate_prompt()
        
        assert result['stage'] == WorkflowGuide.STAGE_DATA_GENERATION
        assert 'generate_mock_data' in result['nextActions']
        assert '5' in result['prompt']

    def test_generate_validation_prompt(self, workflow_guide):
        """Test validation stage prompt generation"""
        workflow_guide.start_workflow()
        for _ in range(6):  # Advance to validation
            workflow_guide.advance_stage()
        
        workflow_guide.update_data({'generated_data_count': 10})
        
        result = workflow_guide.generate_prompt()
        
        assert result['stage'] == WorkflowGuide.STAGE_VALIDATION
        assert 'validate_mock_data' in result['nextActions']
        assert '10' in result['prompt']

    def test_generate_correction_prompt(self, workflow_guide):
        """Test correction stage prompt generation"""
        workflow_guide.start_workflow()
        for _ in range(7):  # Advance to correction
            workflow_guide.advance_stage()
        
        workflow_guide.update_data({
            'validation_issues': [
                'Time mismatch between prometheus and logging',
                'Memory values out of range'
            ]
        })
        
        result = workflow_guide.generate_prompt()
        
        assert result['stage'] == WorkflowGuide.STAGE_CORRECTION
        assert 'Time mismatch' in result['prompt']
        assert 'Memory values' in result['prompt']

    def test_generate_completed_prompt(self, workflow_guide):
        """Test completed stage prompt generation"""
        workflow_guide.start_workflow()
        for _ in range(8):  # Advance to completed
            workflow_guide.advance_stage()
        
        workflow_guide.update_data({'scenario_id': 'scenario_abc123'})
        
        result = workflow_guide.generate_prompt()
        
        assert result['stage'] == WorkflowGuide.STAGE_COMPLETED
        assert result['progress'] == 100
        assert 'save_scenario' in result['nextActions']
        assert 'scenario_abc123' in result['prompt']

    def test_workflow_persistence(self, workflow_guide, db):
        """Test that workflow state persists across instances"""
        # Create and advance workflow
        workflow_guide.start_workflow()
        workflow_guide.update_data({'test': 'persistence'})
        workflow_guide.advance_stage()
        
        # Create new instance with same database
        new_guide = WorkflowGuide(db)
        state = new_guide.get_current_state()
        
        assert state is not None
        assert state.stage == WorkflowGuide.STAGE_TARGET_COLLECTION
        assert state.data['test'] == 'persistence'

    def test_history_tracking(self, workflow_guide):
        """Test that history is properly tracked"""
        workflow_guide.start_workflow()
        workflow_guide.update_data({'key1': 'value1'})
        workflow_guide.advance_stage()
        workflow_guide.update_data({'key2': 'value2'})
        workflow_guide.add_plot_suggestion({'type': 'test'})
        
        state = workflow_guide.get_current_state()
        
        # Should have multiple history entries
        assert len(state.history) >= 5
        
        # Check event types
        event_types = [entry['event_type'] for entry in state.history]
        assert 'workflow_started' in event_types
        assert 'data_updated' in event_types
        assert 'stage_advanced' in event_types
        assert 'plot_suggestion_added' in event_types

    def test_complete_workflow_cycle(self, workflow_guide):
        """Test a complete workflow cycle"""
        # Start
        state = workflow_guide.start_workflow()
        assert state.stage == WorkflowGuide.STAGE_INIT
        
        # Progress through all stages
        stages_visited = [state.stage]
        while state.stage != WorkflowGuide.STAGE_COMPLETED:
            state = workflow_guide.advance_stage()
            stages_visited.append(state.stage)
        
        # Verify all stages were visited in order
        assert stages_visited == WorkflowGuide.STAGE_ORDER
        assert workflow_guide.get_progress() == 100

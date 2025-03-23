/**
 * @file model-controls.tsx
 * @description
 *   Component that provides controls for model selection, temperature adjustment,
 *   and starting new chat conversations.
 *
 * @features
 *   - Model selection dropdown with display names
 *   - Temperature adjustment slider with visual feedback
 *   - New chat button to reset conversation
 *   - Responsive layout for mobile and desktop views
 *   - Disabled state handling during streaming responses
 *   - Accessible controls with appropriate ARIA attributes
 * 
 * @dependencies
 *   - React for component architecture
 *   - Ant Design for UI components (Select, Button, Slider)
 *   - ModelConfig type from useChatState hook
 * 
 * @implementation
 *   The component renders a responsive container with three main elements:
 *   a button for starting new chats, a dropdown for selecting AI models, and
 *   a slider for adjusting temperature. It's fully controlled with state management
 *   handled by the parent component via props.
 */

import React from 'react';
import { Select, Button, Slider } from 'antd';
import { ModelConfig } from '../hooks/useChatState';

interface ModelControlsProps {
  selectedModel: string;
  setSelectedModel: (value: string) => void;
  models: ModelConfig[];
  temperature: number;
  setTemperature: (value: number) => void;
  isStreaming: boolean;
  handleNewChat: () => void;
}

/**
 * Renders controls for model selection, temperature adjustment, and new chat creation
 * 
 * @param props - Component properties including model state, handlers and configuration
 * @returns A responsive control panel for chat configuration
 */
export default function ModelControls({
  selectedModel,
  setSelectedModel,
  models,
  temperature,
  setTemperature,
  isStreaming,
  handleNewChat,
}: ModelControlsProps) {
  const { Option } = Select;

  return (
    <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between mb-4">
      <div>
        <Button
          type="primary"
          onClick={handleNewChat}
          disabled={isStreaming}
          aria-label="Start a new chat"
          size="middle"
        >
          New Chat
        </Button>
      </div>

      <div className="flex flex-col">
        <Select
          id="modelSelect"
          value={selectedModel}
          onChange={(value) => setSelectedModel(value)}
          disabled={isStreaming}
          style={{
            minWidth: '200px',
            height: '40px'
          }}
          dropdownStyle={{ minWidth: '250px', maxHeight: '300px' }}
          aria-label="Select AI model"
          size="middle"
        >
          {models.map((m) => (
            <Option key={m.deployment_name} value={m.deployment_name}>
              {m.display_name}
            </Option>
          ))}
        </Select>
      </div>

      <div className="flex items-center" style={{ width: '220px' }}>
        <div className="text-sm font-medium mr-2 whitespace-nowrap" style={{ width: '80px' }}>
          Temp: {temperature.toFixed(1)}
        </div>
        <Slider
          min={0}
          max={2}
          step={0.1}
          value={temperature}
          onChange={(value) => setTemperature(value)}
          disabled={isStreaming}
          tooltip={{ formatter: (value) => `${value?.toFixed(1)}` }}
          aria-label={`Temperature value: ${temperature.toFixed(1)}`}
          style={{ flex: 1 }}
        />
      </div>
    </div>
  );
}
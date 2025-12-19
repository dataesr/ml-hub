import { useState } from "react";
import validator from "@rjsf/validator-ajv8";
import { Pipeline } from "../../../api/pipelines/types";
import { useRunPipeline } from "../../../api/pipelines/hooks";
import { Button } from "@dataesr/dsfr-plus";
import JsonSchemaForm from "../../../components/rjsf-form";


interface PipelineFormProps {
  pipeline: Pipeline;
}
export default function PipelineForm({ pipeline }: PipelineFormProps) {
  const { mutate: runPipeline, isLoading, isSuccess, error } = useRunPipeline();
  const [formData, setFormData] = useState<any>({});

  const schema = { "type": "object", "properties": pipeline.inputs }

  const handleSubmit = ({ formData }: { formData: any }) => {
    runPipeline({ name: pipeline.pipeline, data: formData });
  };
  if (isSuccess) {
    return (
      <div className="p-4 bg-green-500/10 text-green-400 border border-green-500/20 rounded">
        <p>Pipeline <strong>{pipeline.pipeline}</strong> launched successfully!</p>
        <Button onClick={() => window.location.reload()} size="sm" variant="text" className="mt-2">Launch Another</Button>
      </div>
    );
  }
  if (!pipeline.inputs) {
    return <div className="text-gray-400">Inputs configuration required.</div>;
  }
  return (
    <div className="pipeline-form rjsf-dark-theme">
      {error && <div className="p-2 mb-2 text-red-400 bg-red-500/10 border border-red-500/20 rounded">Failed to launch pipeline</div>}
      <JsonSchemaForm
        schema={schema}
        validator={validator}
        formData={formData}
        onChange={(e) => setFormData(e.formData)}
        onSubmit={handleSubmit}
        uiSchema={{
          "ui:title": pipeline.pipeline,
          "ui:description": pipeline.description,
          "ui:classNames": "pipeline-form",
          "ui:submitButtonOptions": {
            "props": {
              "disabled": false,
              "className": "fr-btn fr-btn--secondary"
            },
            "norender": false,
            "submitText": "Launch Pipeline"
          }
        }}
        className="text-white"
      />
    </div>
  );
}

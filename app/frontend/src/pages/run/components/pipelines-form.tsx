import { useState } from "react";
import validator from "@rjsf/validator-ajv8";
import { Pipeline } from "../../../api/pipelines/types";
import { useRunPipeline } from "../../../api/pipelines/hooks";
import { Alert, Button, Container } from "@dataesr/dsfr-plus";
import JsonSchemaForm from "../../../components/rjsf-form";


interface PipelineFormProps {
  pipeline: Pipeline;
}
export default function PipelineForm({ pipeline }: PipelineFormProps) {
  const { mutate: runPipeline, isSuccess, error } = useRunPipeline()
  const [formData, setFormData] = useState<any>({});

  const handleSubmit = ({ formData }: { formData: any }) => {
    runPipeline({ name: pipeline.pipeline, data: formData });
  };
  if (isSuccess) {
    return (
      <Container fluid>
        <Alert variant="success" title="Success" description={`Pipeline ${pipeline.pipeline} launched successfully!`} />
        <Button onClick={() => window.location.reload()} size="sm" variant="tertiary" className="fr-mt-2w">Launch Another</Button>
      </Container>
    );
  }
  if (!pipeline.inputs) {
    return <Alert variant="warning" title="No Inputs" description="Inputs configuration required." />
  }
  return (
    <Container fluid>
      {error && <Alert variant="error" title="Error" description="Failed to launch pipeline" />}
      <JsonSchemaForm
        schema={pipeline.inputs}
        validator={validator}
        formData={formData}
        onChange={(e) => setFormData(e.formData)}
        onSubmit={handleSubmit}
        uiSchema={{
          "ui:title": pipeline.pipeline,
          "ui:submitButtonOptions": {
            "norender": false,
            "submitText": "Launch Pipeline"
          }
        }}
      />
    </Container>
  );
}

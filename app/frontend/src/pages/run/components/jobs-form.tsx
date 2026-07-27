import { useState } from "react"
import validator from "@rjsf/validator-ajv8"
import { Job } from "../../../api/jobs/types"
import { useRunJob } from "../../../api/jobs/hooks"
import { Alert, Button, Container } from "@dataesr/dsfr-plus"
import JsonSchemaForm from "../../../components/rjsf-form"

interface JobFormProps {
  job: Job
}
export default function JobForm({ job }: JobFormProps) {
  const { mutate: runJob, isSuccess, error } = useRunJob()
  const [formData, setFormData] = useState<any>({})

  const handleSubmit = ({ formData }: { formData: any }) => {
    runJob({ name: job.name, data: formData })
  }
  if (isSuccess) {
    return (
      <Container fluid>
        <Alert variant="success" title="Success" description={`Job ${job.name} launched successfully!`} />
        <Button onClick={() => window.location.reload()} size="sm" variant="tertiary" className="fr-mt-2w">
          Launch Another
        </Button>
      </Container>
    )
  }
  if (!job.inputs) {
    return <Alert variant="warning" title="No Inputs" description="Inputs configuration required." />
  }
  return (
    <Container fluid>
      {error && <Alert variant="error" title="Error" description="Failed to launch job" />}
      <JsonSchemaForm
        schema={job.inputs}
        validator={validator}
        formData={formData}
        onChange={(e) => setFormData(e.formData)}
        onSubmit={handleSubmit}
        uiSchema={{
          "ui:title": job.name,
          "ui:submitButtonOptions": {
            norender: false,
            submitText: "Launch Job",
          },
        }}
      />
    </Container>
  )
}

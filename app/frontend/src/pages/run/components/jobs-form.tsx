import { useState } from "react"
import type { IChangeEvent } from "@rjsf/core"
import validator from "@rjsf/validator-ajv8"
import { Job } from "../../../api/jobs/types"
import { useRunJob } from "../../../api/jobs/hooks"
import { Alert, Button, Container } from "@dataesr/dsfr-plus"
import JsonSchemaForm from "../../../components/rjsf-form"

interface JobFormProps {
  job: Job
  onClose?: () => void
}
export default function JobForm({ job, onClose }: JobFormProps) {
  const { mutate: runJob, isSuccess, isLoading, error, reset } = useRunJob()
  const [formData, setFormData] = useState<any>({})

  const handleSubmit = (data: IChangeEvent<any>) => {
    runJob({ name: job.name, data: data.formData ?? {} })
  }

  if (isSuccess) {
    return (
      <Container fluid className="fr-px-0">
        <Alert variant="success" title="Success" description={`Job ${job.name} launched successfully!`} />
        <div className="fr-mt-2w">
          <Button
            onClick={() => {
              reset()
              setFormData({})
            }}
            size="sm"
            variant="secondary"
            className="fr-mr-2w"
          >
            Launch again
          </Button>
          {onClose ? (
            <Button onClick={onClose} size="sm" variant="tertiary">
              Choose another job
            </Button>
          ) : null}
        </div>
      </Container>
    )
  }

  if (!job.inputs) {
    return <Alert variant="warning" title="No Inputs" description="Inputs configuration required." />
  }

  return (
    <Container fluid className="fr-px-0">
      {error && <Alert variant="error" title="Error" description="Failed to launch job" />}
      <JsonSchemaForm
        schema={job.inputs}
        validator={validator}
        formData={formData}
        onChange={(e) => setFormData(e.formData ?? {})}
        onSubmit={handleSubmit}
        disabled={isLoading}
        uiSchema={{
          "ui:description": "Fill in the fields below to start a new execution.",
          "ui:submitButtonOptions": {
            norender: false,
            submitText: isLoading ? "Launching..." : "Launch job",
          },
        }}
      />
    </Container>
  )
}

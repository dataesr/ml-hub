import { useState } from "react"
import { apiJobsCreate } from "../../api"
import { Accordion, Button, Checkbox, Container, Select, SelectOption, TextInput, Title, Toggle } from "@dataesr/dsfr-plus"
import { OvhAiJob, OvhAiJobInputs } from "../../types/jobs"
import { scrollToTop } from "../../utils"
import { useNavigate } from "react-router-dom"

const DEFAULT_INPUTS: OvhAiJobInputs = {
  name: "",
  model_name: "",
  dataset_name: "",
  gpu: 1,
}

export default function JobsSubmit() {
  const [inputs, setInputs] = useState<OvhAiJobInputs>(DEFAULT_INPUTS)
  const [pushToHF, setPushToHF] = useState<boolean>(false)
  const jobType = "finetuning"
  const navigate = useNavigate()

  const resetInputs = () => {
    setPushToHF(false)
    setInputs(DEFAULT_INPUTS)
    scrollToTop()
  }

  const handleInputsChange = (key: string, value: any) => setInputs({ ...inputs, [key]: value })

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      const newJob: OvhAiJob = await apiJobsCreate(inputs)
      console.log("newJob", newJob)
      resetInputs()
    } catch (error) {
      console.error("Error creating job:", error)
      alert("Error creating job. Please try again.")
    } finally {
    }
  }

  console.log("inputs", inputs)

  return (
    <Container className="fr-my-3w">
      <Button size="sm" variant="tertiary" icon="arrow-left-line" onClick={() => navigate("/jobs")}>
        Back to jobs
      </Button>
      <Title as="h2" className="fr-mb-4w fr-mt-5w">
        New training job
      </Title>
      <Container fluid style={{ maxWidth: "600px" }}>
        <Select label="Job Type" defaultSelectedKey={jobType} isDisabled>
          <SelectOption key={"finetuning"}>Finetuning</SelectOption>
        </Select>
        <TextInput
          label="Job Name"
          hint="Name of the job. Not unique but should be descriptive."
          value={inputs.name}
          onChange={(e) => handleInputsChange("name", e.target.value)}
          required
        />
        <TextInput
          label="Model Name"
          hint="HuggingFace repository of the model to train."
          value={inputs.model_name}
          onChange={(e) => handleInputsChange("model_name", e.target.value)}
          required
        />
        <TextInput
          label="Dataset Name"
          hint="HuggingFace repository or OVH file path of the dataset."
          value={inputs.dataset_name}
          onChange={(e) => handleInputsChange("dataset_name", e.target.value)}
          required
        />
        <Toggle
          label="Run job on GPU"
          checked={Boolean(inputs.gpu)}
          onChange={(e) => handleInputsChange("gpu", Number(e.target.checked))}
        />
        <Toggle label="Push model on HuggingFace" checked={pushToHF} onChange={(e) => setPushToHF(e.target.checked)} />
        {pushToHF && (
          <Container fluid className="fr-ml-5w fr-mt-2w">
            <TextInput
              label="HuggingFace Name"
              hint="Name of the HuggingFace repository to push the model."
              value={inputs?.hf_hub || ""}
              required={pushToHF}
              onChange={(e) => handleInputsChange("hf_hub", e.target.value)}
            />
            <Checkbox
              label="Make the repository private"
              checked={inputs?.hf_hub_private || true}
              onChange={(e) => handleInputsChange("hf_hub_private", e.target.checked)}
            />
          </Container>
        )}
        <Accordion title="Advanced options" className="fr-mt-5w">
          <Select
            label="Dataset prompts format"
            defaultSelectedKey={"auto"}
            selectedKey={inputs?.dataset_format || "auto"}
            onSelectionChange={(key) => handleInputsChange("dataset_format", key)}
          >
            <SelectOption key="auto">Auto</SelectOption>
            <SelectOption key="text">Text</SelectOption>
            <SelectOption key="conversational">Conversational</SelectOption>
          </Select>
          <Toggle
            label="Link OVH dataset volume"
            checked={inputs?.dataset_volume || false}
            onChange={(e) => handleInputsChange("dataset_volume", e.target.checked)}
          />
          <TextInput
            className="fr-mt-2w"
            label="W&B Run Name"
            hint="Name of the W&B run. Automatically generated if not set."
            value={inputs?.wandb_name || ""}
            onChange={(e) => handleInputsChange("wandb_name", e.target.value)}
          />
          <TextInput
            label="W&B Project Name"
            hint="Name of the W&B project. Defaults to 'huggingface' if not set."
            value={inputs?.wandb_project || ""}
            onChange={(e) => handleInputsChange("wandb_project", e.target.value)}
          />
          <Toggle
            label="Disable W&B"
            checked={inputs?.wandb_disabled}
            onChange={(e) => handleInputsChange("wandb_disabled", e.target.checked)}
          />
        </Accordion>
        <div className="fr-mt-5w" style={{ display: "flex", width: "100%", alignItems: "center" }}>
          <div style={{ flexGrow: 1 }}>
            <Button variant="secondary" onClick={() => resetInputs()}>
              Reset options
            </Button>
          </div>
          <Button onClick={onSubmit}>Create job</Button>
        </div>
      </Container>
    </Container>
  )
}

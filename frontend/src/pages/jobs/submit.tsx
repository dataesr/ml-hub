import { useEffect, useState } from "react"
import {
  Accordion,
  Alert,
  Button,
  Checkbox,
  Container,
  Modal,
  ModalContent,
  ModalFooter,
  ModalTitle,
  Select,
  SelectOption,
  Text,
  TextArea,
  TextInput,
  Title,
  Toggle,
} from "@dataesr/dsfr-plus"
import { scrollToTop } from "../../utils"
import { useNavigate } from "react-router-dom"
import { validateDebouncedInput, validateInput } from "./helpers/validate"
import { Job, JobInputs } from "../../api/jobs/types"
import { createJob } from "../../api/jobs/api"

const DEFAULT_INPUTS: JobInputs = {
  name: "",
  model_name: "",
  dataset_name: "",
  gpu: 1,
}

export default function JobsSubmit() {
  const [inputs, setInputs] = useState<JobInputs>(DEFAULT_INPUTS)
  const [pushToHF, setPushToHF] = useState<boolean>(false)
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [alertError, setAlertError] = useState<string>("")
  const [alertSuccess, setAlertSuccess] = useState<string>("")
  const [openSubmit, setOpenSubmit] = useState<boolean>(false)
  const debouncedTimersRef = useState<Record<string, number>>({})[0]
  const navigate = useNavigate()
  const jobType = "finetuning"
  const required = inputs.name && inputs.model_name && inputs.dataset_name && ((pushToHF && inputs?.hf_hub) || !pushToHF)

  const resetInputs = () => {
    setPushToHF(false)
    setInputs(DEFAULT_INPUTS)
    setErrors({})
    scrollToTop()
  }

  const handleErrorsChange = (key: string, message: string) => {
    if (message) {
      setErrors((prev) => ({ ...prev, [key]: message }))
    } else if (key in errors) {
      const { [key]: _, ...newErrors } = errors
      setErrors(newErrors)
    }
  }

  const handleInputsChange = (key: string, value: any) => {
    setInputs({ ...inputs, [key]: value })
    setAlertError("")

    if (debouncedTimersRef[key]) {
      clearTimeout(debouncedTimersRef[key])
    }

    // keys that may trigger API calls
    if (["model_name", "dataset_name", "hf_hub"].includes(key)) {
      debouncedTimersRef[key] = setTimeout(async () => {
        const message = await validateDebouncedInput(key, value)
        handleErrorsChange(key, message)
      }, 1500)
    } else {
      const message = validateInput(key, value)
      handleErrorsChange(key, message)
    }
  }

  const handlePushToHFChange = (push: boolean) => {
    if (!push) {
      const { hf_hub, hf_hub_private, ...newInputs } = inputs
      setInputs(newInputs)
    }
    setPushToHF(push)
  }

  const onCheck = (e: React.FormEvent) => {
    e.preventDefault()
    if (Object.entries(errors).length) setAlertError("Please fix the errors before creating the job.")
    else setOpenSubmit(true)
  }

  const onSubmit = async () => {
    try {
      const newJob: Job = await createJob(inputs)
      resetInputs()
      setAlertSuccess(`Successfully created job ${newJob.spec.name} (${newJob.id})`)
      setTimeout(() => navigate(`/jobs`), 2000)
    } catch (error) {
      console.error("Error creating job:", error)
      setAlertError("Error creating job. Please try again.")
    }
  }

  useEffect(() => {
    return () => Object.values(debouncedTimersRef).forEach((t) => t && clearTimeout(t))
  }, [])

  console.log("input", inputs)
  console.log("errors", errors)

  return (
    <Container className="fr-my-3w">
      <Button size="sm" variant="tertiary" icon="arrow-left-line" onClick={() => navigate("/jobs")}>
        Back to jobs
      </Button>
      <Title as="h2" className="fr-mb-4w fr-mt-5w">
        New training job
      </Title>
      <Container fluid style={{ maxWidth: "600px" }}>
        <Select label="Job Type" defaultSelectedKey={jobType}>
          <SelectOption key={"finetuning"}>Finetuning</SelectOption>
        </Select>
        <TextInput
          label="Job Name"
          hint="Name of the job. Not unique but should be descriptive."
          value={inputs.name}
          onChange={(e) => handleInputsChange("name", e.target.value)}
          maxLength={64}
          required
          messageType={errors.name ? "error" : undefined}
          message={errors.name || undefined}
        />
        <TextInput
          label="Model Name"
          hint="HuggingFace repository of the model to train."
          value={inputs.model_name}
          onChange={(e) => handleInputsChange("model_name", e.target.value)}
          required
          messageType={errors.model_name ? "error" : undefined}
          message={errors.model_name || undefined}
        />
        <TextInput
          label="Dataset Name"
          hint="HuggingFace repository or OVH file path of the dataset."
          value={inputs.dataset_name}
          onChange={(e) => handleInputsChange("dataset_name", e.target.value)}
          required
          messageType={errors.dataset_name ? "error" : undefined}
          message={errors.dataset_name || undefined}
        />
        <Toggle
          label="Run job on GPU"
          checked={Boolean(inputs.gpu)}
          onChange={(e) => handleInputsChange("gpu", Number(e.target.checked))}
        />
        <Toggle
          label="Push model on HuggingFace"
          checked={pushToHF}
          onChange={(e) => handlePushToHFChange(e.target.checked)}
        />
        {pushToHF && (
          <Container fluid className="fr-ml-5w fr-mt-2w">
            <TextInput
              label="HuggingFace Name"
              hint="Name of the HuggingFace repository to push the model."
              value={inputs?.hf_hub || ""}
              onChange={(e) => handleInputsChange("hf_hub", e.target.value)}
              required={pushToHF}
              messageType={errors.hf_hub ? "error" : undefined}
              message={errors.hf_hub || undefined}
            />
            <Checkbox
              label="Make the repository private"
              checked={inputs?.hf_hub_private || false}
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
          <TextArea
            style={{ resize: "vertical", maxHeight: "400px" }}
            className="fr-mt-2w"
            label="Dataset prompts instruction"
            hint="Custom instruction that will be applied to all prompts."
            value={inputs?.dataset_instruction || ""}
            placeholder="You are a helpful assistant..."
            onChange={(e) => handleInputsChange("dataset_instruction", e.target.value)}
            messageType={errors.dataset_instruction ? "error" : undefined}
            message={errors.dataset_instruction || undefined}
          />
          <TextInput
            className="fr-mt-2w"
            label="Dataset prompts text format"
            hint="Text format that will be applied to all prompts."
            value={inputs?.dataset_text_format || ""}
            placeholder="### Instruction:\n {instruction}..."
            onChange={(e) => handleInputsChange("dataset_text_format", e.target.value)}
            messageType={errors.dataset_text_format ? "error" : undefined}
            message={errors.dataset_text_format || undefined}
          />
          <TextInput
            className="fr-mt-2w"
            label="Dataset prompts chat template"
            hint="Chat template that will be applied to all prompts."
            value={inputs?.dataset_text_format || ""}
            placeholder="{%- for message in messages -%}..."
            onChange={(e) => handleInputsChange("dataset_chat_template", e.target.value)}
            messageType={errors.dataset_chat_template ? "error" : undefined}
            message={errors.dataset_chat_template || undefined}
          />
          <Toggle
            label="Link OVH dataset volume"
            checked={inputs?.dataset_volume || false}
            onChange={(e) => handleInputsChange("dataset_volume", e.target.checked)}
          />
          <hr />
          <TextInput
            className="fr-mt-2w"
            label="W&B Run Name"
            hint="Name of the W&B run. Automatically generated if not set."
            value={inputs?.wandb_name || ""}
            onChange={(e) => handleInputsChange("wandb_name", e.target.value)}
            messageType={errors.wandb_name ? "error" : undefined}
            message={errors.wandb_name || undefined}
          />
          <TextInput
            label="W&B Project Name"
            hint="Name of the W&B project. Defaults to 'huggingface' if not set."
            value={inputs?.wandb_project || ""}
            onChange={(e) => handleInputsChange("wandb_project", e.target.value)}
            messageType={errors.wandb_project ? "error" : undefined}
            message={errors.wandb_project || undefined}
          />
          <Toggle
            label="Disable W&B"
            checked={inputs?.wandb_disabled}
            onChange={(e) => handleInputsChange("wandb_disabled", e.target.checked)}
          />
        </Accordion>
        {alertError && (
          <Alert
            className="fr-mt-4w"
            variant="error"
            title="Error"
            description={alertError}
            closeMode="controlled"
            onClose={() => setAlertError("")}
          />
        )}
        <div className="fr-mt-5w" style={{ display: "flex", width: "100%", alignItems: "center" }}>
          <div style={{ flexGrow: 1 }}>
            <Button variant="secondary" onClick={() => resetInputs()} disabled={inputs === DEFAULT_INPUTS}>
              Reset options
            </Button>
          </div>
          <Button onClick={onCheck} disabled={!required}>
            Create job
          </Button>
        </div>
        <Container fluid>
          <Modal isOpen={openSubmit} hide={() => null}>
            <ModalTitle>Confirm job</ModalTitle>
            <ModalContent>
              <Text>Are you sure you want to submit the following job ?</Text>
              <Text className="fr-mb-1v fr-text--legend">{`- type: ${jobType}`}</Text>
              {Object.entries(inputs).map(([key, value]) => (
                <Text className="fr-mb-1v fr-text--legend">{`- ${key}: ${String(value)}`}</Text>
              ))}
            </ModalContent>
            <ModalFooter>
              {alertSuccess ? (
                <Alert variant="success" title="Job created!" description={alertSuccess} />
              ) : (
                <div className="fr-mt-5w" style={{ display: "flex", width: "100%", alignItems: "center" }}>
                  <div style={{ flexGrow: 1 }}>
                    <Button variant="secondary" onClick={() => setOpenSubmit(false)}>
                      No
                    </Button>
                  </div>
                  <Button onClick={onSubmit}>Create</Button>
                </div>
              )}
            </ModalFooter>
          </Modal>
        </Container>
      </Container>
    </Container>
  )
}

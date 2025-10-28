import { useState } from "react"
import { TrainNewJobArgs } from "../../../types/train"
import { apiJobsCreate } from "../../../api"
import {
  Button,
  Checkbox,
  Container,
  Modal,
  ModalClose,
  ModalContent,
  ModalTitle,
  Select,
  SelectOption,
  Text,
  TextInput,
  Toggle,
} from "@dataesr/dsfr-plus"

interface TrainNewModalProps {
  isOpen: boolean
  onClose: () => void
}

export function JobsNew({ isOpen, onClose }: TrainNewModalProps) {
  const [formData, setFormData] = useState<TrainNewJobArgs>({
    name: "",
    model_name: "",
    dataset_name: "",
    gpu: 1,
  })
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false)
  const [pushToHF, setPushToHF] = useState<boolean>(false)

  const resetForm = () => setFormData({ name: "", model_name: "", dataset_name: "" })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)

    try {
      const res = await apiJobsCreate(formData)
      console.log("res", res)
      onClose()
      resetForm()
    } catch (error) {
      console.error("Error creating job:", error)
      alert("Error creating job. Please try again.")
    } finally {
      setIsSubmitting(false)
    }
  }

  const addEnvVar = () => {
    setFormData({
      ...formData,
      envs: [...formData.envs, { name: "", value: "" }],
    })
  }

  const updateEnvVar = (index: number, field: "name" | "value", value: string) => {
    const newEnvs = [...formData.envs]
    newEnvs[index] = { ...newEnvs[index], [field]: value }
    setFormData({ ...formData, envs: newEnvs })
  }

  const removeEnvVar = (index: number) => {
    setFormData({
      ...formData,
      envs: formData.envs.filter((_, i) => i !== index),
    })
  }

  const handleFormChange = (key: string, value: any) => setFormData({ ...formData, [key]: value })

  return (
    <Modal size="lg" isOpen={isOpen} hide={onClose}>
      <ModalClose>Close</ModalClose>
      <ModalTitle>New training job</ModalTitle>
      <ModalContent>
        <form onSubmit={handleSubmit}>
          <TextInput
            label="Job Name"
            hint="Name of the job. Not unique but should be descriptive."
            value={formData.name}
            onChange={(e) => handleFormChange("name", e.target.value)}
            required
          />
          <TextInput
            label="Model Name"
            hint="HuggingFace repository of the model to train."
            value={formData.model_name}
            onChange={(e) => handleFormChange("name", e.target.value)}
            required
          />
          <TextInput
            label="Dataset Name"
            hint="HuggingFace repository or ovh file path."
            value={formData.dataset_name}
            onChange={(e) => handleFormChange("dataset_name", e.target.value)}
            required
          />
          <Checkbox
            label="Push the trained model to huggingface"
            checked={pushToHF}
            onChange={(e) => setPushToHF(e.target.checked)}
          />
          {pushToHF && (
            <Container fluid className="fr-ml-5w fr-mt-2w">
              <TextInput
                label="HuggingFace Name"
                hint="Name of the HuggingFace repository to push the model."
                value={formData?.hf_hub || ""}
                onChange={(e) => handleFormChange("hf_hub", e.target.value)}
              />
              <Checkbox
                label="Make the repository private"
                checked={formData?.hf_hub_private || true}
                onChange={(e) => handleFormChange("hf_hub_private", e.target.checked)}
              />
            </Container>
          )}
          <Text size="md">Advanced params</Text>
          <TextInput
            label="Number of GPU"
            hint="Number of GPU to use."
            type="number"
            min={0}
            max={10}
            value={formData.gpu}
            onChange={(e) => Number(e.target.value) > 0 && handleFormChange("gpu", e.target.value)}
          />
          <Select label="Dataset messages format" defaultSelectedKey={"auto"}>
            <SelectOption key="auto">auto</SelectOption>
          </Select>
          <Toggle label="Link dataset volume" />
          <Text size="md">Environment variables</Text>
          {/*

          <div className="fr-fieldset">
            <legend className="fr-fieldset__legend">Environment Variables</legend>
            {formData.envs.map((env, index) => (
              <div
                key={index}
                className="fr-fieldset__element"
                style={{ display: "flex", gap: "1rem", marginBottom: "1rem", alignItems: "flex-end" }}
              >
                <div className="fr-input-group" style={{ flex: 1 }}>
                  <label className="fr-label" htmlFor={`env-name-${index}`}>
                    Name
                  </label>
                  <input
                    className="fr-input"
                    id={`env-name-${index}`}
                    type="text"
                    placeholder="Variable name"
                    value={env.name}
                    onChange={(e) => updateEnvVar(index, "name", e.target.value)}
                  />
                </div>
                <div className="fr-input-group" style={{ flex: 1 }}>
                  <label className="fr-label" htmlFor={`env-value-${index}`}>
                    Value
                  </label>
                  <input
                    className="fr-input"
                    id={`env-value-${index}`}
                    type="text"
                    placeholder="Variable value"
                    value={env.value}
                    onChange={(e) => updateEnvVar(index, "value", e.target.value)}
                  />
                </div>
                <Button
                  icon="delete-bin-line"
                  variant="secondary"
                  onClick={() => removeEnvVar(index)}
                  disabled={isSubmitting}
                  type="button"
                >
                  Remove
                </Button>
              </div>
            ))}
            <Button type="button" variant="secondary" onClick={addEnvVar} disabled={isSubmitting}>
              Add Environment Variable
            </Button>
          </div>

          <div style={{ display: "flex", gap: "1rem", marginTop: "2rem" }}>
            <button className="fr-btn" type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Creating..." : "Create Job"}
            </button>
            <button className="fr-btn fr-btn--secondary" type="button" onClick={onClose} disabled={isSubmitting}>
              Cancel
            </button>
          </div> */}
        </form>
      </ModalContent>
    </Modal>
  )
}

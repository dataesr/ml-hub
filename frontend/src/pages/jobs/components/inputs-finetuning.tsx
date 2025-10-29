import { useEffect, useState } from "react"
import { hfGetRepository } from "../../../helpers"
import { Container, TextInput } from "@dataesr/dsfr-plus"

const isValidName = (value: string) => /^[A-Za-z0-9._-]+$/.test(value)
const isValidRepoName = (value: string) => /^[^\/\s]+\/[^^\s]+$/.test(value)
const isValidText = (value: any) => typeof value === "string" && String(value).trim().length > 0
const requiredFieldMessage = "This field is required."
const invalidNameMessage = "Only alphanumeric characters, underscores, hyphens and dots are allowed."
const isValidRepo = async (name: string, type: "model" | "dataset") => {
  const repo = await hfGetRepository(name, type)
  return repo?.id
}
const invalidRepoNameMessage = ""
const repoNotFoundMessage = "Repository not found on HuggingFace."

interface inputArgs<T> {
  currentValue: T
  onChange: (name: string, value: string) => void
}
const validateInput = (value: string) => (value === "attention" ? "ok" : "error")

export function InputJobName({ currentValue, onChange }: inputArgs<string>) {
  const [input, setInput] = useState<string>(currentValue)
  const [errorMessage, setErrorMessage] = useState<string>("")

  useEffect(() => {
    if (input != currentValue) {
      if (!isValidName(input)) setErrorMessage(invalidNameMessage)
      else setErrorMessage("")
      const timer = setTimeout(() => {
        onChange("name", input)
      }, 1000)
      return () => {
        clearTimeout(timer)
      }
    }
  }, [input])

  return (
    <TextInput
      label="Job Name"
      hint="Name of the job. Not unique but should be descriptive."
      value={input}
      onChange={(e) => setInput(e.target.value)}
      maxLength={64}
      required
      messageType={errorMessage ? "error" : undefined}
      message={errorMessage || undefined}
    />
  )
}

export function InputModelName({ currentValue, onChange }: inputArgs<string>) {
  const [input, setInput] = useState<string>(currentValue)
  const [errorMessage, setErrorMessage] = useState<string>("")

  useEffect(() => {
    async function findRepo(name: string) {
      return await isValidRepo(name, "model")
    }
    if (input != currentValue) {
      const timer = setTimeout(() => {
        console.log("isValidRepoName", isValidRepoName(input))
        if (isValidRepoName(input)) {
          if (!findRepo(input)) setErrorMessage(repoNotFoundMessage)
        } else {
          setErrorMessage(invalidRepoNameMessage)
        }
        onChange("model_name", input)
      }, 1000)
      return () => {
        clearTimeout(timer)
      }
    }
  }, [input])

  return (
    <TextInput
      label="Model Name"
      hint="HuggingFace repository of the model to train."
      value={input}
      onChange={(e) => setInput(e.target.value)}
      required
      messageType={errorMessage ? "error" : undefined}
      message={errorMessage || undefined}
    />
  )
}

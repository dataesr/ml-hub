import { hfGetRepository } from "."

const requiredFieldMessage = "This field is required."
const invalidNameMessage = "Only alphanumeric characters, underscores, hyphens and dots are allowed."
const invalidRepoNameMessage = "Incorrect repository name, should be <owner>/<model_name>"
const invalidRepoOwnerMessage = (owner: string) => `Incorrect repository name, should be ${owner}/<model_name>`
const repoNotFoundMessage = "Repository not found on HuggingFace."

const isValidText = (value: any) => typeof value === "string" && String(value).trim().length > 0
const isValidAlphaNum = (value: string) => /^[A-Za-z0-9._-]+$/.test(value)
const isValidRepoName = (text: string, owner?: string) => {
  const pattern = `^${owner ? owner : "[a-zA-Z0-9._-]+"}/[a-zA-Z0-9._-]+$`
  return new RegExp(pattern).test(text)
}

export const validateText = (value: string, required?: boolean) => {
  if (required && !isValidText(value)) return requiredFieldMessage
}

export const validateAplhaNum = (value: string, required?: boolean) => {
  if (required && !isValidText(value)) return requiredFieldMessage
  if (isValidText(value)) {
    if (!isValidAlphaNum(value)) return invalidNameMessage
  }
}

export const validateRepoName = async (value: string, required?: boolean, exists?: boolean, owner?: string) => {
  if (required && !isValidText(value)) return requiredFieldMessage
  if (isValidText(value)) {
    if (!isValidRepoName(value, owner)) {
      return owner ? invalidRepoOwnerMessage(owner) : invalidRepoNameMessage
    } else {
      if (exists) {
        const repo = await hfGetRepository(value, "model").catch(() => undefined)
        if (!repo?.id) return repoNotFoundMessage
      }
    }
  }
}

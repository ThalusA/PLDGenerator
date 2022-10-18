import {Octokit} from 'octokit'
import * as fs from 'node:fs'
import {program} from 'commander'

import {PLDSchema, UserStory} from './pld'

function bodyFromUserStory(userStory: UserStory): string {
  return (`

`)
}

function bodyFromPLD(pld: PLDSchema): string {
  return (`

`)
}

function checkIfIssueNumberInBody(issueNumber: number, body?: string): boolean {
  if (body === undefined) {
    return false
  }

  return body.includes(`- [x] #${issueNumber}`)
}

interface Options {
  token: string
  owner: string
  repo: string
}

program
  .option('-t, --token <token>', 'GitHub Token')
  .option('-o, --owner <owner>', 'GitHub Owner')
  .option('-r, --repo <repo>', 'GitHub Repo')
  .version('0.0.1')

program
  .command('export <filepath>')
  .description('Export PLD as a JSON file to <filepath> from GitHub Issues')
  .action(async (filepath: string, options: Options) => {})

program
  .command('import <filepath>')
  .description('Import PLD from a JSON file located at <filepath> to GitHub Issues')
  .action(async (filepath: string, options: Options) => {
    const octokit = new Octokit({auth: options.token})

    const pld: PLDSchema = JSON.parse(fs.readFileSync(filepath, 'utf8'))

    enum labels {
      UserStory = 'user-story',
      Deliverable = 'deliverable',
      Subset = 'subset',
      PLD = 'pld',
    }

    const labelPromises = []
    for (const label of Object.values(labels)) {
      labelPromises.push(octokit.rest.issues.getLabel({
        owner: options.owner,
        repo: options.repo,
        name: label,
      }).catch(() => octokit.rest.issues.createLabel({
        owner: options.owner,
        repo: options.repo,
        name: label,
      })))
    }

    await Promise.all(labelPromises)

    const availableIssues: Record<string, Awaited<ReturnType<typeof octokit.rest.issues.list>>['data'][0] | Awaited<ReturnType<typeof octokit.rest.issues.create>>['data']> = {}
    const issueIterator = octokit.paginate.iterator(octokit.rest.issues.list, {
      owner: options.owner,
      repo: options.repo,
      per_page: 100,
    })
    for await (const {data: issues} of issueIterator) {
      for (const issue of issues) {
        availableIssues[issue.title.split(' ', 2)[0]] = issue
      }
    }

    const savedPLD = availableIssues[pld.title] ?? await octokit.rest.issues.create({
      owner: options.owner,
      repo: options.repo,
      title: pld.title,
      labels: [labels.PLD],
      body: bodyFromPLD(pld),
    }).then(response => response.data)
    const deliverables = []
    if (pld.deliverables) {
      let deliverableDepth = 1
      for (const deliverable of pld.deliverables) {
        const savedDeliverable = availableIssues[`${deliverableDepth}`] ?? await octokit.rest.issues.create({
          owner: options.owner,
          repo: options.repo,
          title: `${deliverableDepth} ${deliverable.name}`,
          labels: [labels.Deliverable],
          body: deliverable.description,
        }).then(response => response.data)
        deliverables.push(savedDeliverable)
        const subsets = []

        if (deliverable.subsets) {
          let subsetDepth = 1
          for (const subset of deliverable.subsets) {
            const savedSubset = availableIssues[`${deliverableDepth}.${subsetDepth}`] ?? await octokit.rest.issues.create({
              owner: options.owner,
              repo: options.repo,
              title: `${deliverableDepth}.${subsetDepth} ${subset.name}`,
              labels: [labels.Subset],
              body: subset.description,
            }).then(response => response.data)
            subsets.push(savedSubset)
            const user_stories = []
            if (subset.user_stories) {
              let userStoryDepth = 1
              for (const userStory of subset.user_stories) {
                const savedUserStory = availableIssues[`${deliverableDepth}.${subsetDepth}.${userStoryDepth}`] ?? await octokit.rest.issues.create({
                  owner: options.owner,
                  repo: options.repo,
                  title: `${deliverableDepth}.${subsetDepth}.${userStoryDepth} ${userStory.name}`,
                  labels: [labels.UserStory],
                  body: bodyFromUserStory(userStory),
                }).then(response => response.data)
                user_stories.push(savedUserStory)
                await octokit.rest.issues.update({
                  owner: options.owner,
                  repo: options.repo,
                  issue_number: savedUserStory.number,
                  title: `${deliverableDepth}.${subsetDepth}.${userStoryDepth} ${userStory.name}`,
                  labels: [labels.UserStory],
                  body: bodyFromUserStory(userStory),
                })
                userStoryDepth += 1
              }
            }

            await octokit.rest.issues.update({
              owner: options.owner,
              repo: options.repo,
              issue_number: savedSubset.number,
              title: `${deliverableDepth}.${subsetDepth} ${subset.name}`,
              labels: [labels.Subset],
              body: subset.description ? subset.description + user_stories.map(userStory => `\n- [${checkIfIssueNumberInBody(userStory.number, savedSubset.body_text) ? 'x' : ' '}] #${userStory.number}`) : undefined,
            })

            subsetDepth += 1
          }
        }

        await octokit.rest.issues.update({
          owner: options.owner,
          repo: options.repo,
          issue_number: savedDeliverable.number,
          title: `${deliverableDepth} ${deliverable.name}`,
          labels: [labels.Deliverable],
          body: deliverable.description ? deliverable.description + subsets.map(subset => `\n- [${checkIfIssueNumberInBody(subset.number, savedDeliverable.body_text) ? 'x' : ' '}] #${subset.number}`) : undefined,
        })

        deliverableDepth += 1
      }
    }

    await octokit.rest.issues.update({
      owner: options.owner,
      repo: options.repo,
      issue_number: savedPLD.number,
      title: `${savedPLD.title}`,
      labels: [labels.PLD],
      body: pld.description ? bodyFromPLD(pld) + deliverables.map(deliverable => `\n- [${checkIfIssueNumberInBody(deliverable.number, savedPLD.body_text) ? 'x' : ' '}] #${deliverable.number}`) : undefined,
    })
  })

program.parse()

import {Octokit} from 'octokit'
import fs from 'node:fs/promises'
import {program} from 'commander'

import {PLDSchema} from './pld'
import {LocaleDictionary} from './locale'
import {bodyFromPLD, bodyFromDeliverable, bodyFromSubset, bodyFromUserStory, pldFromBody} from './transformer'
import {CreatedIssue, Issue, Labels, Options, PLDTree} from './types'

program
  .enablePositionalOptions()

program
  .requiredOption('-t, --token <token>', 'GitHub Token')
  .requiredOption('-o, --owner <owner>', 'GitHub Owner')
  .requiredOption('-r, --repo <repo>', 'GitHub Repo')
  .version('0.1.0')

program
  .command('export <filepath>')
  .description('Export PLD as a JSON file to <filepath> from GitHub Issues')
  .passThroughOptions()
  .action(async (filepath: string) => {
    const options: Options = program.opts()

    const octokit = new Octokit({auth: options.token})
    const issueIterator = octokit.paginate.iterator(octokit.rest.issues.listForRepo, {
      owner: options.owner,
      repo: options.repo,
      per_page: 100,
    })
    const availableIssues: PLDTree = {}
    for await (const {data: issues} of issueIterator) {
      for (const issue of issues) {
        if (issue.labels.find(label => (typeof label === 'string' ? label : label.name) === Labels.PLD)) {
          availableIssues["0"] = issue
        } else if (issue.labels.find(label => (typeof label === 'string' ? label : label.name) === Labels.Deliverable)) {
          const [deliverable] = issue.title.split(' ')[0].split('.')
          if (availableIssues[deliverable] === undefined) {
            availableIssues[deliverable] = {}
          }
          availableIssues[deliverable]["0"] = issue
        } else if (issue.labels.find(label => (typeof label === 'string' ? label : label.name) === Labels.Subset)) {
          const [deliverable, subset] = issue.title.split(' ')[0].split('.')
          if (availableIssues[deliverable] === undefined) {
            availableIssues[deliverable] = {}
          }
          if (availableIssues[deliverable][subset] === undefined) {
            availableIssues[deliverable][subset] = {}
          }
          availableIssues[deliverable][subset]["0"] = issue
        } else if (issue.labels.find(label => (typeof label === 'string' ? label : label.name) === Labels.UserStory)) {
          const [deliverable, subset, userStory] = issue.title.split(' ')[0].split('.')
          if (availableIssues[deliverable] === undefined) {
            availableIssues[deliverable] = {}
          }
          if (availableIssues[deliverable][subset] === undefined) {
            availableIssues[deliverable][subset] = {}
          }
          availableIssues[deliverable][subset][userStory] = issue
        }
      }
    }

    const localeLiteral = (availableIssues["0"]?.body ?? '').match(/<th>Localisation<\/th>\s*<td>(?<locale>[^<]+)<\/td>/)?.groups?.locale
    if (localeLiteral === undefined) {
      throw new Error("Couldn't find the locale")
    }
    const locale: LocaleDictionary = JSON.parse(await fs.readFile(`../src/locale/${localeLiteral}.json`, 'utf8'))

    const pld = pldFromBody(locale, availableIssues)
    const schema = {  "$schema": "https://raw.githubusercontent.com/ThalusA/PLDGenerator/master/pld_schema.json",}
    await fs.writeFile(filepath, JSON.stringify({...schema, ...pld}, null, 2))
  })

program
  .command('import <filepath>')
  .description('Import PLD from a JSON file located at <filepath> to GitHub Issues')
  .passThroughOptions()
  .action(async (filepath: string) => {
    const options: Options = program.opts()

    const octokit = new Octokit({auth: options.token})

    const pld: PLDSchema = JSON.parse(await fs.readFile(filepath, 'utf8'))
    const locale: LocaleDictionary = JSON.parse(await fs.readFile(`../src/locale/${pld.locale}.json`, 'utf8'))

    const labelPromises = []
    for (const label of Object.values(Labels)) {
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

    const availableIssues: Record<string, Issue & CreatedIssue> = {}
    const issueIterator = octokit.paginate.iterator(octokit.rest.issues.listForRepo, {
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
      labels: [Labels.PLD],
      body: bodyFromPLD(locale, pld),
    }).then(response => response.data)
    const deliverables: Array<Issue & CreatedIssue> = []
    if (pld.deliverables) {
      for (const deliverable of pld.deliverables) {
        const savedDeliverable = availableIssues[`${deliverables.length + 1}`] ?? await octokit.rest.issues.create({
          owner: options.owner,
          repo: options.repo,
          title: `${deliverables.length + 1} ${deliverable.name}`,
          labels: [Labels.Deliverable],
          body: bodyFromDeliverable(locale, deliverable),
        }).then(response => response.data)
        deliverables.push(savedDeliverable)
        const subsets: Array<Issue & CreatedIssue> = []

        if (deliverable.subsets) {
          for (const subset of deliverable.subsets) {
            const savedSubset = availableIssues[`${deliverables.length + 1}.${subsets.length + 1}`] ?? await octokit.rest.issues.create({
              owner: options.owner,
              repo: options.repo,
              title: `${deliverables.length + 1}.${subsets.length + 1} ${subset.name}`,
              labels: [Labels.Subset],
              body: subset.description,
            }).then(response => response.data)
            subsets.push(savedSubset)
            const userStories: Array<Issue & CreatedIssue> = []
            if (subset.user_stories) {
              for (const userStory of subset.user_stories) {
                const savedUserStory = availableIssues[`${deliverables.length + 1}.${subsets.length + 1}.${userStories.length + 1}`] ?? await octokit.rest.issues.create({
                  owner: options.owner,
                  repo: options.repo,
                  title: `${deliverables.length + 1}.${subsets.length + 1}.${userStories.length + 1} ${userStory.name}`,
                  labels: [Labels.UserStory],
                  body: bodyFromUserStory(locale, userStory),
                }).then(response => response.data)
                userStories.push(savedUserStory)
              }
            }

            await octokit.rest.issues.update({
              owner: options.owner,
              repo: options.repo,
              issue_number: savedSubset.number,
              title: `${deliverables.length + 1}.${subsets.length + 1} ${subset.name}`,
              labels: [Labels.Subset],
              body: bodyFromSubset(locale, subset, savedSubset, userStories),
            })
          }
        }

        await octokit.rest.issues.update({
          owner: options.owner,
          repo: options.repo,
          issue_number: savedDeliverable.number,
          title: `${deliverables.length + 1} ${deliverable.name}`,
          labels: [Labels.Deliverable],
          body: bodyFromDeliverable(locale, deliverable, savedDeliverable, subsets),
        })
      }
    }

    await octokit.rest.issues.update({
      owner: options.owner,
      repo: options.repo,
      issue_number: savedPLD.number,
      title: `${savedPLD.title}`,
      labels: [Labels.PLD],
      body: bodyFromPLD(locale, pld, savedPLD, deliverables),
    })
  })

program.parse()

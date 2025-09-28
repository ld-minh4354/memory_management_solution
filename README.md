# Memory Management: Solution - Minh Le

We explain our proposed approach to memory management of the information of existing tool calls, in order to control the size of the agent's input and to minimize repeated tool calls due to forgetting. We will first summarize the current approach to memory management. We will then explain our main two main ideas to improve memory management. We will finally briefly explain our implementation of part of the ideas.

Due to the time constraint, we have only implemented part of our ideas, and opted to include other ideas and details in this document. We hope that this is an acceptable choice to convey our ideas in as much details as possible.

## Summary and Analysis of Current Approach

The current memory management system treats the information of each tool call (we will call each of this a "trace") independently from each other. The system summarizes and compresses each trace to reduce the size of the input being passed to the agent.

In addition, in order to ensure that important information are conveyed, the system may choose to selectively expand certain trace to its original full form, and provide this full information to the agent.

In our solution, we focus on the two following areas of improvement of the current system:

- Traces are treatred independently. This means that if there are multiple calls of creation, edition, execution and/or deletion of the same code file, we are unable to combine those information to create more succint and updated summaries/compressions.

- The size of the input still grows linearly with the number of trace. Assumming there is a strict upper bound of the size of the agent's input, this approach is not sustainable forever. Even if there is no strict upper bound, excessive information is likely to reduce the agent's performance, making it degrade over time.

We address each of these areas of improvement in Ideas 1 and 2, respectively.

## Idea 1: Code File Summary

The main high level motivation is this: In the current approach, traces are treated as the main "object" of concern. This is evident as traces are the main nodes in the knowledge graph database used to store information. However, in our proposed approach, we will also have code files as another type of "object" of concern. We will have a summary for each file, and every time a tool is used on that file, we will update this summary.

There are multiple benefits to this approach:

- It **combines the information of all relevant tool calls** to a file, including create_file, modify_code, run_file, and delete_file. This allows us to further reduce the size of the input passed into the agent.

- It is possible that an update to the file overwrites (fully or partially) a previous update. In this case, our summary update should **overwrite outdated information with new information**, further reducing the input size. An extreme example of this is that when the file is deleted, its summary can simply state that the file has been deleted.

## Idea 2: Time-based and Priority-based Information Deletion

We note that traces are still being treated as one of the main "object" of concern, because tools like execute_command, search_internet, etc. can't be meaningfully associated together into an object. Thus, to address the linearly growing size of input, we inevitably need to delete some traces. The main question, of course, is how do we select traces to delete.

We identify two factors that can contribute to the importance/relevance of a trace:

- How likely are information in a trace will be used in the future.

- Whether the trace is from a recent (or old) tool call. Recent traces are more likely to contain information that will be used in the next timestep.

Our main idea is therefore to **quantify the importance of a trace**, and allow the **trace's importance decay** over time. We will then delete the trace with the lowest importance when needed. The decay of the traces can be linear or exponential, or any other functions found suitable.

There are two details to be worked out with approach.

### Quantification of Traces' Importance

The easiest way is to just call the OpenAI's API and ask it to give a number on how likely the provided information will be used in the future.

If we want to improve the performance of this, we can finetune the model as follows:

- Get a list of real traces being used, without any memory compression.

- For each trace, identify which future traces need its information. This can be done by using the OpenAI's API to compare pairs of traces.

- We now have the traces and their "importance". We can use this to finetune the OpenAI model, or even train our own LLM.

### Efficient Data Structure

We are essentially using a priority queue, where existing weights in the queue decay over time. We need an efficient data structure to implement this. We choose a **kinetic priority queue** for this task. For more information, see the paper "Kinetic Hanger" by G. Fonseca, C. Figueiredo, and P. Carvalho.

If the decay is linear, the author of this paper shows that each update takes O(n log n), where n is the number of traces stored in the structure at the same time. Since n is limited by the input size of the agent, the processing time for each trace processing is constantly upper bounded.

If the decay is exponential (which is the more natural idea), the update actually take O(m log n log log n), where m is the total number of elements. This means the update time is not constantly upper bounded, making it unsuitable. This is why we prefer a linear decay, although at first glance it is less intuitive than an exponential decay.

## Being Everything Together & Implementation

To combine the two ideas, we divide the traces into those that modify files and those that do not. We will then maintain and update the former with the first idea, and maintain and update the latter with the second idea.

Due to time constraint, we have only managed to implement the first idea for file creation and edition. Still, we hope that this document has provided sufficient insights into our ideas and motivations.

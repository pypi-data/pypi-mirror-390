# This file is a mockup work in progress not intended for use

# source = [0, 1, 2, 3, 4, 5]

# source = [0, 1 ,      4 ,    7, 8, 9]


# previous_index = index_fiddle(step)
# sample = prior_pipelien.retrieve(previous)
# modified = step.forward(sample)

# cached property


# class PipelineStep():

#     def index_things(self, *args, **query):
#         '''
#         Return the index or query to retrieve from pull operation
#         '''
#         return unchanged_index_or_query

#     def get_valid_indexes():


#     def reverse(self, *args, **kwargs):
#         '''
#         Get the reverse-ordered previous sample
#         Apply the inverse operation
#         Return the result
#         '''
#         raise NotImplementedError

#     def forward(index, previous_steps, rest_of_previous_steps):
#         '''
#         Get the previous sample
#         Apply the operation
#         Return the result
#         '''

#         prior_sample = prev.forward(index, *other_steps)
#         result =  self.apply(prior_sample)
#         return result

#     def apply(input):
#         raise NotImplementedError

#     def inverse():
#         raise NotImplementedError


# class Pipeline(PipelineStep):

#     def __init__(self, steps):

#         self.steps = steps
#         self.final_step = steps[-1]

#     def add(self, step):

#         if isinstance(step, callable):
#             step = _CallableStep(callable)

#         self.steps = self.steps | step


#     def forward(self, query):

#         self.last_element.forward(head, tail)

#     def reverse:
#         self.first

#     def apply(self, query):
#         self.last_element.forward(head, tail)


#     def get_valid_indexes()


# class _CallableStep(PipelineStep):
#     '''
#     Allows callables (i.e. functions and lambdas) to be added
#     as pipeline steps
#     '''

#     def __init__(self, callable):
#         self.callable = callable
#         self.name = 'unnammed'
#         if hasattr(callable, 'name'):
#             self.name = callable.name

#     def forward(self, *args, **kwargs):
#         return self.callable(*args, **kwargs)

#     def reverse(self, *args, **kwargs):
#         raise NotImplementedError(f'Cannot reverse callable-only pipeline step f{self.name}')


# class Cache(PipelineStep):

#     def forward(self, *args, **kwargs):
#         '''
#         Retrieve cached data for the query or index if it exists
#         Otherwise, retrieve it from the upstream pipeline, and cache it
#         '''

# class DataSource(PipelineStep):
#     '''
#     Examples:
#         Fetching model data from disk based on a query like a date-time
#         Generate data such as noise or calculated (e.g. diurnal) data
#         Generate static data (e.g. topography) which is invariant to the query
#         Return a cached version of those things
#     '''

#     def forward(self, None, index_or_query, **other_args):

#         it = go_fetch_it_from_disk(index_or_query)
#         return it


# ------------------


# p1 = ds | op1
# p2 = ds | op | sampler

# for example in p2:
#     something(p2)

# sampler = ForwardPassByDate()
#         = RandomFetchByDate(count=1000, between=slice(2010, 2020))
#         = Shuffler()
#         = RandomIndexer(seed=42)
#         = ForwardPassDropMissing()
#         = ForwadPassFillClimatology()

# sampler = HandCraftedExactIndexer()


# aggregator = DailyToHourly()


# # # Heaps of these
# # class Operation(PipelineStep):
# #     '''
# #     Represents a mathematical or algorithmic transform of the data, such
# #     as a division, a scaling step, a unit conversion. Often reversible.
# #     '''


# # class Model(PipelineStep):
# #     '''
# #     A model which defined a forward operator which can be used in a pipeline.
# #     '''


# # # Maybe 6 of these I can think of
# # class Sampler(PipelineStep):
# #     '''
# #     Something which will implement various strategies for retrieving data
# #     from a pipeline, such as a forward pass, a random sample with or
# #     without replacement, a debiased sample or a biased sample (e.g. selecting
# #     rare events only)
# #     '''

# # # Probably 3-20 of these
# # class Aggregator(PipelineStep):
# #     '''
# #     Examples:

# #         Something to calculate a rolling mean of the last n inputs
# #         Something to generate minibatches of samples for training
# #         Something to yield data subsets from a larger source object
# #         Something to turn a per-sample query into a sequence-to-sequence query
# #     '''

# #     # Replaces "modifications"
# #     # Replaces temporalretrieval
# #     pass
